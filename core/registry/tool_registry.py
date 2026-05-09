"""
core/registry/tool_registry.py

OCP: no orchestrator code changes needed when adding new tools.
"""
from core.interfaces.base_tool import BaseTool, ReversibilityLevel


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_all(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_by_reversibility(self, level: ReversibilityLevel) -> list[BaseTool]:
        return [t for t in self._tools.values() if t.reversibility == level]

    def get_schemas(self) -> list[dict]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def list_names(self) -> list[str]:
        return list(self._tools.keys())
