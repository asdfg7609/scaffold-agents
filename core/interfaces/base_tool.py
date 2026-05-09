"""
core/interfaces/base_tool.py

Common contract for tools. Used when wrapping per-framework in adapters/.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ReversibilityLevel(Enum):
    """
    Reversibility level of a tool's action.
    Determines the execution gate in system/reversibility_guard.py.
    """
    GREEN  = "green"   # Fully reversible (reads/queries) → auto-execute
    YELLOW = "yellow"  # Partially reversible (create/modify) → audit log required
    RED    = "red"     # Irreversible (delete/send) → human approval required


@dataclass
class ToolResult:
    """Tool execution result — framework-agnostic common type"""
    success: bool
    output: str
    error: str = ""
    metadata: dict = field(default_factory=dict)


class BaseTool(ABC):
    """Common interface for all tool implementations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (snake_case recommended; referenced by LLM when calling)"""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description — the only documentation the LLM reads. Max 1024 chars."""
        ...

    @property
    @abstractmethod
    def reversibility(self) -> ReversibilityLevel:
        """Reversibility level — used to determine the execution gate"""
        ...

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool. Calls pure functions in domain/tools/."""
        ...
