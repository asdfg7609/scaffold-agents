"""
adapters/langgraph/tools.py

Wraps pure functions from domain/tools/ as LangGraph @tool format.
Does not touch business logic in domain/.
"""


def get_langgraph_tools() -> list:
    try:
        from langchain_core.tools import tool
    except ImportError:
        raise ImportError("pip install langgraph langchain-anthropic")

    from domain.tools.green.search import search_news, read_url
    from domain.tools.yellow.write_file import write_file, read_file, list_files

    @tool
    def langgraph_search_news(query: str, max_results: int = 5) -> str:
        """Search for news. Use when: you need the latest information on a specific topic."""
        return str(search_news(query=query, max_results=max_results))

    @tool
    def langgraph_read_url(url: str) -> str:
        """Read the body content of a URL."""
        return str(read_url(url=url))

    @tool
    def langgraph_write_file(filename: str, content: str) -> str:
        """Save a file. Use when: you need to save output to a file. ⚠️ YELLOW level."""
        return str(write_file(filename=filename, content=content))

    @tool
    def langgraph_list_files() -> str:
        """Return the list of saved files."""
        return str(list_files())

    return [langgraph_search_news, langgraph_read_url, langgraph_write_file, langgraph_list_files]
