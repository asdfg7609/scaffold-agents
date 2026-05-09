"""
agents/research_agent.py — Information search specialist agent (SRP)
"""
from core.interfaces.base_agent import BaseAgent, AgentResult
from core.llm.base_llm import BaseLLM
from core.utils.retry import with_retry
from core.utils.logger import get_logger
from domain.prompts.researcher import RESEARCHER_SYSTEM_PROMPT
from domain.tools.green.search import search_news

logger = get_logger(__name__)


class ResearchAgent(BaseAgent):
    """Handles only search and information gathering. Analysis and reports are other agents' roles."""

    def __init__(self, llm: BaseLLM):
        self.llm = llm   # DIP: depends on abstract interface, not a concrete implementation

    def get_name(self)        -> str: return "research_agent"
    def get_description(self) -> str: return "Searches news and information on a given topic."
    def get_capabilities(self) -> list[str]: return ["web_search", "news_search", "information_retrieval"]

    def run(self, input: str, session_id: str = "default") -> AgentResult:
        logger.info(f"[ResearchAgent] Starting search: {input[:50]}")
        try:
            # 1. Search with tool
            search_result = with_retry(fn=lambda: search_news(query=input, max_results=5))

            # 2. Summarize with LLM
            response = with_retry(fn=lambda: self.llm.chat(
                messages=[{"role": "user", "content": f"Query: {input}\n\nResults:\n{search_result}"}],
                system=RESEARCHER_SYSTEM_PROMPT,
                max_tokens=2000,
            ))
            return AgentResult(
                output=response.content, success=True,
                metadata={"model": response.model, "tokens": response.input_tokens + response.output_tokens},
            )
        except Exception as e:
            logger.error(f"[ResearchAgent] Error: {e}")
            return AgentResult(output="", success=False, error=str(e))
