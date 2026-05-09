"""
memory/redis_store.py — Production Redis implementation + memory factory.
Same interface as InMemoryStore → swap without code changes (LSP).
"""
import json
import os
from datetime import datetime
from core.interfaces.base_memory import BaseMemory, AgentState


class RedisStore(BaseMemory):
    KEY_PREFIX  = "agent:state:"
    DEFAULT_TTL = 60 * 60 * 24  # 24 hours

    def __init__(self, ttl: int = DEFAULT_TTL):
        try:
            import redis
            self.client = redis.from_url(
                os.environ.get("REDIS_URL", "redis://localhost:6379"),
                decode_responses=True,
            )
            self.ttl = ttl
        except ImportError:
            raise ImportError("pip install redis")

    def _key(self, sid: str) -> str:
        return f"{self.KEY_PREFIX}{sid}"

    def get_state(self, session_id: str) -> AgentState:
        raw = self.client.get(self._key(session_id))
        if raw is None:
            return AgentState(session_id=session_id)
        d = json.loads(raw)
        s = AgentState(session_id=session_id)
        s.messages     = d.get("messages", [])
        s.current_goal = d.get("current_goal", "")
        s.todo_list    = d.get("todo_list", [])
        return s

    def save_state(self, state: AgentState) -> None:
        data = {
            "session_id":   state.session_id,
            "messages":     state.messages,
            "current_goal": state.current_goal,
            "todo_list":    state.todo_list,
            "last_updated": datetime.now().isoformat(),
        }
        self.client.setex(self._key(state.session_id), self.ttl, json.dumps(data))

    def delete_state(self, session_id: str) -> None:
        self.client.delete(self._key(session_id))


def create_memory_store() -> BaseMemory:
    """Environment-variable-based memory factory."""
    backend = os.environ.get("MEMORY_BACKEND", "in_memory")
    if backend == "redis":
        return RedisStore()
    from memory.in_memory_store import InMemoryStore
    return InMemoryStore()
