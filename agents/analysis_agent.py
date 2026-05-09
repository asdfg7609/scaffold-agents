"""
agents/analysis_agent.py — Data analysis specialist agent (SRP)
"""
from core.interfaces.base_agent import BaseAgent, AgentResult
from core.llm.base_llm import BaseLLM
from core.utils.retry import with_retry
from core.utils.logger import get_logger
from domain.prompts.analyst import ANALYST_SYSTEM_PROMPT

logger = get_logger(__name__)


class AnalysisAgent(BaseAgent):
    """Analyzes collected information to extract insights. Search and reports are other agents' roles."""

    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def get_name(self)        -> str: return "analysis_agent"
    def get_description(self) -> str: return "Analyzes collected information to extract insights and trends."
    def get_capabilities(self) -> list[str]: return ["data_analysis", "trend_detection", "insight_extraction"]

    def run(self, input: str, session_id: str = "default") -> AgentResult:
        logger.info(f"[AnalysisAgent] Starting analysis: {input[:50]}")
        try:
            response = with_retry(fn=lambda: self.llm.chat(
                messages=[{"role": "user", "content": f"Analyze the following information:\n\n{input}"}],
                system=ANALYST_SYSTEM_PROMPT,
                max_tokens=2000,
            ))
            return AgentResult(output=response.content, success=True, metadata={"model": response.model})
        except Exception as e:
            logger.error(f"[AnalysisAgent] Error: {e}")
            return AgentResult(output="", success=False, error=str(e))
