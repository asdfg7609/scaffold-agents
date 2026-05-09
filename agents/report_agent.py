"""
agents/report_agent.py — Report writing and saving specialist agent (SRP)
"""
from core.interfaces.base_agent import BaseAgent, AgentResult
from core.llm.base_llm import BaseLLM
from core.utils.retry import with_retry
from core.utils.logger import get_logger
from domain.prompts.analyst import REPORTER_SYSTEM_PROMPT
from domain.tools.yellow.write_file import write_file
from datetime import datetime

logger = get_logger(__name__)


class ReportAgent(BaseAgent):
    """Handles only report writing and file saving."""

    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def get_name(self)        -> str: return "report_agent"
    def get_description(self) -> str: return "Writes analysis results as a markdown report and saves it to a file."
    def get_capabilities(self) -> list[str]: return ["report_writing", "document_creation", "file_saving"]

    def run(self, input: str, session_id: str = "default") -> AgentResult:
        logger.info("[ReportAgent] Starting report writing")
        try:
            response = with_retry(fn=lambda: self.llm.chat(
                messages=[{"role": "user", "content": f"Write the following analysis results as a markdown report:\n\n{input}"}],
                system=REPORTER_SYSTEM_PROMPT,
                max_tokens=3000,
            ))
            content  = response.content
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            saved    = write_file(filename=filename, content=content)

            if not saved.get("success"):
                return AgentResult(output=content, success=False, error=f"File save failed: {saved.get('error')}")

            return AgentResult(
                output=content, success=True,
                metadata={"file_path": saved.get("path"), "filename": filename, "word_count": len(content.split())},
            )
        except Exception as e:
            logger.error(f"[ReportAgent] Error: {e}")
            return AgentResult(output="", success=False, error=str(e))
