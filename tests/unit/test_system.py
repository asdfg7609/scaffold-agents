"""
tests/unit/test_system.py

Tests the system layer with a Mock LLM.
Core value of DIP: the full pipeline can be tested without an API key.
"""
from unittest.mock import MagicMock
from core.interfaces.base_agent import BaseAgent, AgentResult
from core.interfaces.base_tool import BaseTool, ReversibilityLevel, ToolResult
from core.llm.base_llm import BaseLLM, LLMResponse
from core.registry.agent_registry import AgentRegistry
from core.registry.tool_registry import ToolRegistry
from memory.in_memory_store import InMemoryStore
from system.orchestrator import Orchestrator
from system.reversibility_guard import ReversibilityGuard
from system.tracer import Tracer


# ── Mock implementations ───────────────────────────────────────────────

class MockLLM(BaseLLM):
    def __init__(self, response="Mock response"):
        self._r = response
    def chat(self, messages, system="", max_tokens=4096, tools=None) -> LLMResponse:
        return LLMResponse(content=self._r, input_tokens=10, output_tokens=20, model="mock")
    def get_model_name(self) -> str: return "mock"


class MockAgent(BaseAgent):
    def __init__(self, succeed=True):
        self._ok = succeed
    def get_name(self)        -> str: return "mock_agent"
    def get_description(self) -> str: return "Mock"
    def run(self, input, session_id="default") -> AgentResult:
        return AgentResult(output=f"result:{input}", success=True) if self._ok \
               else AgentResult(output="", success=False, error="failed")


class MockGreenTool(BaseTool):
    name          = "mock_green"
    description   = "GREEN test tool"
    reversibility = ReversibilityLevel.GREEN
    def execute(self, **kw) -> ToolResult: return ToolResult(success=True, output="green ok")


class MockRedTool(BaseTool):
    name          = "mock_red"
    description   = "RED test tool"
    reversibility = ReversibilityLevel.RED
    def execute(self, **kw) -> ToolResult: return ToolResult(success=True, output="red ok")


# ── Tests ────────────────────────────────────────────────────

class TestToolRegistry:
    def test_register_get(self):
        r = ToolRegistry(); t = MockGreenTool(); r.register(t)
        assert r.get("mock_green") is t

    def test_ocp(self):
        r = ToolRegistry(); r.register(MockGreenTool()); r.register(MockRedTool())
        assert len(r.get_all()) == 2

    def test_filter_by_reversibility(self):
        r = ToolRegistry(); r.register(MockGreenTool()); r.register(MockRedTool())
        assert len(r.get_by_reversibility(ReversibilityLevel.GREEN)) == 1


class TestReversibilityGuard:
    def setup_method(self): self.tracer = Tracer()

    def test_green_auto(self):
        g = ReversibilityGuard(self.tracer, None)
        assert g.execute(MockGreenTool()).success is True

    def test_red_blocked_no_hitl(self):
        g = ReversibilityGuard(self.tracer, None)
        r = g.execute(MockRedTool())
        assert r.success is False and "HITL" in r.error

    def test_red_approved(self):
        hitl = MagicMock(); hitl.request_approval.return_value = True
        g = ReversibilityGuard(self.tracer, hitl)
        assert g.execute(MockRedTool()).success is True

    def test_red_rejected(self):
        hitl = MagicMock(); hitl.request_approval.return_value = False
        g = ReversibilityGuard(self.tracer, hitl)
        r = g.execute(MockRedTool())
        assert r.success is False and "rejected" in r.error


class TestOrchestrator:
    def _make(self, agents=None):
        ar = AgentRegistry(); tr = ToolRegistry(); mem = InMemoryStore()
        if agents:
            for a in agents: ar.register(a)
        return Orchestrator(ar, tr, mem)

    def test_not_found(self):
        r = self._make().run("test", "nonexistent")
        assert not r.success and "not found" in r.error

    def test_success_saves_session(self):
        orch = self._make([MockAgent(succeed=True)])
        r    = orch.run("hello", "mock_agent", session_id="s1")
        assert r.success
        state = orch.memory.get_state("s1")
        assert len(state.messages) == 2

    def test_pipeline_stops_on_failure(self):
        orch    = self._make([MockAgent(succeed=False)])
        results = orch.run_pipeline("input", ["mock_agent", "mock_agent"])
        assert len(results) == 1 and not results[0].success

    def test_lsp_llm_swap(self):
        from agents.research_agent import ResearchAgent
        a1 = ResearchAgent(llm=MockLLM("response1"))
        a2 = ResearchAgent(llm=MockLLM("response2"))
        assert a1.get_name() == a2.get_name()
