"""
core/registry/agent_registry.py

Agent registration and lookup.
The orchestrator finds agents through this registry and delegates tasks to them.
"""
from core.interfaces.base_agent import BaseAgent


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.get_name()] = agent

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def get_all(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def get_descriptions(self) -> dict[str, str]:
        return {n: a.get_description() for n, a in self._agents.items()}

    def list_names(self) -> list[str]:
        return list(self._agents.keys())
