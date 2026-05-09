"""
tests/unit/test_memory.py — Memory layer unit tests
"""
from core.interfaces.base_memory import AgentState
from memory.in_memory_store import InMemoryStore


class TestAgentState:

    def test_sliding_window(self):
        s = AgentState(session_id="t")
        for i in range(25):
            s.add_message("user", f"msg{i}")
        assert len(s.messages) == s.MAX_WINDOW
        assert s.messages[-1]["content"] == "msg24"

    def test_todo_lifecycle(self):
        s = AgentState(session_id="t")
        tid = s.add_todo("search")
        assert s.todo_list[0]["status"] == "pending"
        s.update_todo(tid, "in_progress")
        assert s.todo_list[0]["status"] == "in_progress"
        s.update_todo(tid, "done", "completed")
        assert s.todo_list[0]["result"] == "completed"


class TestInMemoryStore:

    def setup_method(self):
        self.store = InMemoryStore()

    def test_auto_create(self):
        s = self.store.get_state("new")
        assert s.session_id == "new"
        assert s.messages == []

    def test_save_and_load(self):
        s = self.store.get_state("s1")
        s.add_message("user", "hello")
        self.store.save_state(s)
        loaded = self.store.get_state("s1")
        assert loaded.messages[0]["content"] == "hello"

    def test_session_isolation(self):
        s = self.store.get_state("a")
        s.add_message("user", "message for a")
        self.store.save_state(s)
        assert self.store.get_state("b").messages == []

    def test_delete(self):
        s = self.store.get_state("del")
        s.add_message("user", "to be deleted")
        self.store.save_state(s)
        self.store.delete_state("del")
        assert self.store.get_state("del").messages == []
