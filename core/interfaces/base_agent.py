"""
core/interfaces/base_agent.py

DIP: the orchestrator depends only on this abstract interface.
This file does not change when swapping models or frameworks.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AgentResult:
    """Agent execution result — framework-agnostic common type"""
    output: str
    success: bool
    error: str = ""
    metadata: dict = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations.
    SRP: each implementation performs a single role.
    LSP: every implementation is substitutable via this interface.
    """

    @abstractmethod
    def run(self, input: str, session_id: str = "default") -> AgentResult:
        """Single entry point for the agent."""
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Agent name (used for registry lookup and logging)"""
        ...

    @abstractmethod
    def get_description(self) -> str:
        """One-sentence description of what this agent does."""
        ...

    def get_capabilities(self) -> list[str]:
        """Task types this agent can handle (for A2A Agent Card). Default: empty list."""
        return []
