"""
system/reversibility_guard.py

Reversibility-based execution gate.
GREEN → auto-execute | YELLOW → audit log then execute | RED → HITL approval then execute
"""
from core.interfaces.base_tool import BaseTool, ReversibilityLevel, ToolResult
from system.tracer import Tracer
from core.utils.logger import get_logger

logger = get_logger(__name__)


class ReversibilityGuard:
    def __init__(self, tracer: Tracer, hitl_handler=None):
        self.tracer = tracer
        self.hitl   = hitl_handler

    def execute(self, tool: BaseTool, **kwargs) -> ToolResult:
        level = tool.reversibility
        if level == ReversibilityLevel.GREEN:
            return self._run_green(tool, **kwargs)
        elif level == ReversibilityLevel.YELLOW:
            return self._run_yellow(tool, **kwargs)
        return self._run_red(tool, **kwargs)

    def _run_green(self, tool: BaseTool, **kwargs) -> ToolResult:
        logger.debug(f"[GREEN] {tool.name}")
        return self.tracer.timed_call(tool.name, "tool_call", lambda: tool.execute(**kwargs))

    def _run_yellow(self, tool: BaseTool, **kwargs) -> ToolResult:
        logger.info(f"[YELLOW] {tool.name} — recording audit log")
        return self.tracer.timed_call(
            tool.name, "tool_call", lambda: tool.execute(**kwargs),
            reversibility="yellow", params=str(kwargs),
        )

    def _run_red(self, tool: BaseTool, **kwargs) -> ToolResult:
        logger.warning(f"[RED] {tool.name} — human approval required")
        if self.hitl is None:
            return ToolResult(
                success=False, output="",
                error=f"'{tool.name}' is a RED-level tool. No HITL handler is configured.",
            )
        approved = self.hitl.request_approval(
            tool_name=tool.name, params=kwargs, description=tool.description
        )
        if not approved:
            return ToolResult(success=False, output="", error=f"Human rejected execution of '{tool.name}'.")
        logger.info(f"[RED] {tool.name} — approved")
        return self.tracer.timed_call(
            tool.name, "tool_call", lambda: tool.execute(**kwargs),
            reversibility="red", approved=True,
        )
