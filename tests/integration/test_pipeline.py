"""
tests/integration/test_pipeline.py

Integration tests: validates the full pipeline flow.
Uses the real LLM if ANTHROPIC_API_KEY is set, otherwise falls back to Mock.
"""
import os
from core.registry.agent_registry import AgentRegistry
from core.registry.tool_registry import ToolRegistry
from memory.in_memory_store import InMemoryStore
from system.orchestrator import Orchestrator


def get_test_llm():
    if os.environ.get("ANTHROPIC_API_KEY"):
        from core.llm.claude_llm import ClaudeLLM
        return ClaudeLLM(model="claude-haiku-4-5")
    from tests.unit.test_system import MockLLM
    return MockLLM("Test response: analysis complete. 3 key insights.")


class TestFullPipeline:

    def setup_method(self):
        self.llm    = get_test_llm()
        self.memory = InMemoryStore()
        self.ar     = AgentRegistry()
        self.tr     = ToolRegistry()

    def _orch(self):
        return Orchestrator(self.ar, self.tr, self.memory)

    def test_research_pipeline(self):
        from agents.research_agent  import ResearchAgent
        from agents.analysis_agent  import AnalysisAgent
        self.ar.register(ResearchAgent(self.llm))
        self.ar.register(AnalysisAgent(self.llm))

        results = self._orch().run_pipeline(
            initial_input="Latest AI agent trends",
            pipeline=["research_agent", "analysis_agent"],
            session_id="int_test",
        )
        assert len(results) >= 1
        for r in results:
            assert hasattr(r, "success")

    def test_session_accumulates(self):
        from agents.research_agent import ResearchAgent
        self.ar.register(ResearchAgent(self.llm))
        orch = self._orch()
        orch.run("What is AI?",       "research_agent", session_id="acc")
        orch.run("What is LangGraph?","research_agent", session_id="acc")
        state = self.memory.get_state("acc")
        assert len(state.messages) >= 2

    def test_trace_recorded(self):
        from agents.research_agent import ResearchAgent
        self.ar.register(ResearchAgent(self.llm))
        orch = self._orch()
        orch.run("test", "research_agent")
        s = orch.get_trace_summary()
        assert "run_id" in s and s["total_steps"] >= 1
