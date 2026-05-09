"""
adapters/crewai/tools.py — Wraps domain/tools/ as CrewAI BaseTool
"""


def get_crewai_tools() -> list:
    try:
        from crewai.tools import BaseTool as CrewBaseTool
        from pydantic import BaseModel, Field
    except ImportError:
        raise ImportError("pip install crewai")

    from domain.tools.green.search import search_news
    from domain.tools.yellow.write_file import write_file

    class SearchInput(BaseModel):
        query:       str = Field(description="Search keyword")
        max_results: int = Field(default=5)

    class SearchNewsTool(CrewBaseTool):
        name:        str   = "search_news"
        description: str   = "Search for news. Use when: you need the latest information on a topic."
        args_schema: type  = SearchInput
        def _run(self, query: str, max_results: int = 5) -> str:
            return str(search_news(query=query, max_results=max_results))

    class WriteInput(BaseModel):
        filename: str = Field(description="File name")
        content:  str = Field(description="File content")

    class WriteFileTool(CrewBaseTool):
        name:        str  = "write_file"
        description: str  = "Save a file. Use when: you need to save output to a file."
        args_schema: type = WriteInput
        def _run(self, filename: str, content: str) -> str:
            return str(write_file(filename=filename, content=content))

    return [SearchNewsTool(), WriteFileTool()]
