"""
memory/in_memory_store.py — In-memory implementation for development and testing.
Replace with RedisStore in production (same interface, LSP).
"""
from core.interfaces.base_memory import BaseMemory, AgentState


class InMemoryStore(BaseMemory):
    def __init__(self):
        self._store: dict[str, AgentState] = {}

    def get_state(self, session_id: str) -> AgentState:
        if session_id not in self._store:
            self._store[session_id] = AgentState(session_id=session_id)
        return self._store[session_id]

    def save_state(self, state: AgentState) -> None:
        self._store[state.session_id] = state

    def delete_state(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def list_sessions(self) -> list[str]:
        return list(self._store.keys())
