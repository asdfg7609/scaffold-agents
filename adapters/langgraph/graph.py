"""
adapters/langgraph/graph.py — LangGraph StateGraph definition.
Business logic lives in domain/; only framework glue code belongs here.
"""


def build_research_graph(llm_model: str = "claude-opus-4-5"):
    """Build the research pipeline LangGraph graph."""
    try:
        from typing import TypedDict, Annotated
        from langgraph.graph import StateGraph, END
        from langgraph.prebuilt import ToolNode
        import operator
    except ImportError:
        raise ImportError("pip install langgraph langchain-anthropic")

    from adapters.langgraph.tools import get_langgraph_tools
    from domain.prompts.researcher import RESEARCHER_SYSTEM_PROMPT

    tools     = get_langgraph_tools()
    tool_node = ToolNode(tools)

    class ResearchState(TypedDict):
        messages:      Annotated[list, operator.add]
        final_report:  str

    try:
        from langchain_anthropic import ChatAnthropic
        llm = ChatAnthropic(model=llm_model).bind_tools(tools)
    except ImportError:
        raise ImportError("pip install langchain-anthropic")

    def agent_node(state: ResearchState) -> dict:
        from langchain_core.messages import SystemMessage
        msgs     = [SystemMessage(content=RESEARCHER_SYSTEM_PROMPT)] + state["messages"]
        response = llm.invoke(msgs)
        return {"messages": [response]}

    def should_continue(state: ResearchState) -> str:
        last = state["messages"][-1]
        return "tools" if (hasattr(last, "tool_calls") and last.tool_calls) else END

    graph = StateGraph(ResearchState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")
    return graph.compile()
