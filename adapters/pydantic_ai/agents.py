"""
adapters/pydantic_ai/agents.py — Pydantic AI adapter (type-safe + DI)
"""


def build_pydantic_ai_agent(model: str = "claude-opus-4-5"):
    try:
        from pydantic_ai import Agent, RunContext
        from pydantic import BaseModel
        from dataclasses import dataclass
    except ImportError:
        raise ImportError("pip install pydantic-ai")

    from domain.tools.green.search import search_news
    from domain.tools.yellow.write_file import write_file, list_files
    from domain.prompts.researcher import RESEARCHER_SYSTEM_PROMPT

    @dataclass
    class AgentDeps:
        session_id:  str = "default"
        max_results: int = 5

    class AgentOutput(BaseModel):
        summary:       str
        key_points:    list[str]
        files_created: list[str] = []

    agent = Agent(
        f"anthropic:{model}",
        deps_type=AgentDeps,
        result_type=AgentOutput,
        system_prompt=RESEARCHER_SYSTEM_PROMPT,
    )

    @agent.tool
    async def tool_search_news(ctx: RunContext[AgentDeps], query: str) -> str:
        """Search for news. Use when: you need the latest information on a specific topic."""
        return str(search_news(query=query, max_results=ctx.deps.max_results))

    @agent.tool
    async def tool_write_file(ctx: RunContext[AgentDeps], filename: str, content: str) -> str:
        """Save a file. Use when: you need to save output to a file."""
        return str(write_file(filename=filename, content=content))

    @agent.tool
    async def tool_list_files(ctx: RunContext[AgentDeps]) -> str:
        """Return the list of currently saved files."""
        return str(list_files())

    return agent, AgentDeps
