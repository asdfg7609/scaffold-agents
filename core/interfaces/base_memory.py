"""
core/interfaces/base_memory.py

Common contract for memory backends.
InMemoryStore, RedisStore, etc. implement this interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentState:
    """
    Single source of truth for an agent session.
    Layer 2 principle: agents are stateless; state is delegated to external storage.
    """
    session_id: str
    messages:     list[dict] = field(default_factory=list)
    current_goal: str        = ""
    todo_list:    list[dict] = field(default_factory=list)
    created_at:   datetime   = field(default_factory=datetime.now)
    last_updated: datetime   = field(default_factory=datetime.now)

    MAX_WINDOW: int = 20  # Max messages in short-term memory

    def add_message(self, role: str, content: str) -> None:
        """Manage short-term memory with a sliding window (prevents distractor tokens)."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        if len(self.messages) > self.MAX_WINDOW:
            self.messages = self.messages[-self.MAX_WINDOW:]
        self.last_updated = datetime.now()

    def add_todo(self, description: str) -> str:
        """Add a plan item (Plan-before-Execute principle)."""
        todo_id = f"todo_{len(self.todo_list) + 1}"
        self.todo_list.append({
            "id": todo_id,
            "description": description,
            "status": "pending",   # pending | in_progress | done | failed
            "result": "",
        })
        self.last_updated = datetime.now()
        return todo_id

    def update_todo(self, todo_id: str, status: str, result: str = "") -> None:
        """Update todo item status."""
        for item in self.todo_list:
            if item["id"] == todo_id:
                item["status"] = status
                item["result"] = result
                break
        self.last_updated = datetime.now()


class BaseMemory(ABC):
    """Common interface for memory backends."""

    @abstractmethod
    def get_state(self, session_id: str) -> AgentState:
        """Retrieve session state. Creates a new one if not found."""
        ...

    @abstractmethod
    def save_state(self, state: AgentState) -> None:
        """Save session state."""
        ...

    @abstractmethod
    def delete_state(self, session_id: str) -> None:
        """Delete session state."""
        ...
