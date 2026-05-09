"""
system/orchestrator.py

Framework-agnostic orchestrator.
Depends only on abstract interfaces from core/interfaces/ (DIP).
"""
from core.interfaces.base_agent import BaseAgent, AgentResult
from core.registry.agent_registry import AgentRegistry
from core.registry.tool_registry import ToolRegistry
from core.interfaces.base_memory import BaseMemory
from system.tracer import Tracer
from system.hitl import create_hitl
from system.reversibility_guard import ReversibilityGuard
from core.utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    """
    Agent execution coordinator.
    Responsibilities: agent selection · trust boundary · reversibility gate · tracing · memory management
    """
    def __init__(
        self,
        agent_registry: AgentRegistry,
        tool_registry:  ToolRegistry,
        memory:         BaseMemory,
    ):
        self.agents = agent_registry
        self.tools  = tool_registry
        self.memory = memory
        self.tracer = Tracer()
        self.hitl   = create_hitl()
        self.guard  = ReversibilityGuard(self.tracer, self.hitl)

    def run(
        self,
        task:           str,
        agent_name:     str,
        session_id:     str = "default",
        untrusted_data: list[str] | None = None,
    ) -> AgentResult:
        """Execute the specified agent."""
        logger.info(f"[Orchestrator] '{agent_name}': {task[:50]}...")

        agent = self.agents.get(agent_name)
        if agent is None:
            return AgentResult(
                output="", success=False,
                error=f"Agent '{agent_name}' not found. Registered agents: {self.agents.list_names()}",
            )

        state = self.memory.get_state(session_id)
        state.add_message("user", task)

        result = self.tracer.timed_call(
            step=agent_name, event_type="agent_call",
            fn=lambda: agent.run(task, session_id),
        )

        state.add_message("assistant", result.output if result.success else result.error)
        self.memory.save_state(state)
        return result

    def run_pipeline(
        self,
        initial_input: str,
        pipeline:      list[str],
        session_id:    str = "default",
    ) -> list[AgentResult]:
        """Execute multiple agents in sequence (Prompt Chaining)."""
        results       = []
        current_input = initial_input

        for agent_name in pipeline:
            logger.info(f"[Pipeline] Step: {agent_name}")
            result = self.run(task=current_input, agent_name=agent_name, session_id=session_id)
            results.append(result)

            if not result.success:
                logger.error(f"[Pipeline] '{agent_name}' failed, stopping pipeline")
                break

            current_input = result.output

        return results

    def get_trace_summary(self) -> dict:
        return self.tracer.get_summary()
