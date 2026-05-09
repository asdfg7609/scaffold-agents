"""
domain/tools/green/search.py

GREEN tool: fully reversible (read-only).
Pure Python functions — no import anthropic / import langgraph.
Each framework wraps these in adapters/.
"""
from pydantic import BaseModel, Field


class SearchNewsParams(BaseModel):
    query:       str = Field(description="Keyword or phrase to search for")
    max_results: int = Field(default=5, ge=1, le=20, description="Max number of results (1–20)")


def search_news(query: str, max_results: int = 5) -> dict:
    """
    Search for news articles.
    Use when: you need to gather the latest information on a specific topic.
    Returns: {"query", "total", "results": [{"title","url","summary","published_at"}]}

    Production: connect SerpAPI / Tavily / Bing Search API
    Current: Mock implementation for structural validation
    """
    params = SearchNewsParams(query=query, max_results=max_results)
    results = [
        {
            "title":        f"[{i+1}] News related to {params.query}",
            "url":          f"https://example.com/news/{i+1}",
            "summary":      f"Latest trends summary about {params.query}.",
            "published_at": "2026-05-09",
        }
        for i in range(min(params.max_results, 3))
    ]
    return {"query": params.query, "total": len(results), "results": results}


def read_url(url: str) -> dict:
    """
    Read the body content of a URL.
    Use when: full content analysis of a specific URL is needed.
    Returns: {"url", "title", "content"} or {"error"}
    """
    if not url.startswith(("http://", "https://")):
        return {
            "error": (
                f"Invalid URL: '{url}'. "
                "Must start with http:// or https://."
            )
        }
    return {
        "url":     url,
        "title":   f"Page: {url.split('/')[-1]}",
        "content": f"Body content of {url} (Mock)",
    }
