"""
protocols/a2a/agent_card.py

A2A (Agent-to-Agent) Protocol Agent Card.
Exposed via the /.well-known/agent-card.json endpoint.
"""
import os
import json
from core.registry.agent_registry import AgentRegistry


def generate_agent_card(agent_registry: AgentRegistry) -> dict:
    base_url   = os.environ.get("A2A_BASE_URL",   "http://localhost:8080")
    agent_name = os.environ.get("A2A_AGENT_NAME", "scaffold-agents")

    skills = [
        {"id": a.get_name(), "name": a.get_name().replace("_"," ").title(),
         "description": a.get_description(), "tags": a.get_capabilities()}
        for a in agent_registry.get_all()
    ]
    return {
        "name":        agent_name,
        "description": "Standard AI Agent Project (4-Layer Architecture)",
        "url":         f"{base_url}/a2a",
        "version":     "1.0.0",
        "capabilities": {"streaming": False, "pushNotifications": False, "stateTransitionHistory": True},
        "defaultInputModes":  ["text"],
        "defaultOutputModes": ["text"],
        "skills": skills,
    }


def save_agent_card(agent_registry: AgentRegistry, output_path: str = ".well-known/agent-card.json") -> dict:
    import pathlib
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    card = generate_agent_card(agent_registry)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False, indent=2)
    print(f"Agent Card saved: {output_path}")
    return card
