"""
domain/prompts/shared.py

DRY: common rules shared by all agents.
Loaded from the AGENTS.md file.
"""
from pathlib import Path


def load_agents_md() -> str:
    """Read and return AGENTS.md. Returns a default if not found."""
    p = Path("AGENTS.md")
    if p.exists():
        return p.read_text(encoding="utf-8")
    return """
You perform only the single role you have been assigned.
Confirm with a human before taking any irreversible action.
When uncertain, do not act — ask a clarifying question instead.
""".strip()


COMMON_RULES = load_agents_md()
