"""
system/hitl.py

Human-in-the-Loop approval.
Progressive Autonomy: phased expansion from supervised → semi_auto → autonomous.
"""
import os
from abc import ABC, abstractmethod
from enum import IntEnum


class AutonomyLevel(IntEnum):
    SUPERVISED = 1   # Approval required before every action
    SEMI_AUTO  = 2   # Approval required for RED only
    AUTONOMOUS = 3   # Fully automated


class BaseHITL(ABC):
    @abstractmethod
    def request_approval(self, tool_name: str, params: dict, description: str = "") -> bool:
        ...


class ConsoleHITL(BaseHITL):
    """Terminal-input-based HITL (for development and testing)."""
    def request_approval(self, tool_name: str, params: dict, description: str = "") -> bool:
        print("\n" + "="*50)
        print(f"⚠️  Human Approval Required [RED level]")
        print(f"Tool: {tool_name}")
        print(f"Description: {description}")
        print(f"Parameters: {params}")
        print("="*50)
        while True:
            ans = input("Proceed? (yes/no): ").strip().lower()
            if ans in ("yes","y"): return True
            if ans in ("no","n"):  return False
            print("Please enter 'yes' or 'no'.")


class AutoApproveHITL(BaseHITL):
    """Auto-approve (for tests only — do not use in production)."""
    def request_approval(self, tool_name: str, params: dict, description: str = "") -> bool:
        print(f"[AutoApprove] '{tool_name}' auto-approved (test mode)")
        return True


def create_hitl() -> BaseHITL | None:
    """Environment-variable-based HITL factory."""
    level_str = os.environ.get("AUTONOMY_LEVEL", "supervised")
    level_map  = {"supervised": AutonomyLevel.SUPERVISED, "semi_auto": AutonomyLevel.SEMI_AUTO, "autonomous": AutonomyLevel.AUTONOMOUS}
    level = level_map.get(level_str, AutonomyLevel.SUPERVISED)
    if level == AutonomyLevel.AUTONOMOUS:
        return None
    return ConsoleHITL()
