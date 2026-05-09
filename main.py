"""
main.py — CLI entry point (Composition Root)

Usage:
  python main.py "Research the latest AI agent trends"
  python main.py "What is LangGraph?" --agent research_agent
  python main.py "Write a report" --agent pipeline
  python main.py "AI trends"   --framework langgraph
  python main.py "AI trends"   --framework crewai
  python main.py --eval
  python main.py --mcp
"""
import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()


def build_system():
    """Composition Root — all dependency injection happens here."""
    from core.llm.openai_llm import create_llm
    from core.registry.agent_registry import AgentRegistry
    from core.registry.tool_registry import ToolRegistry
    from memory.redis_store import create_memory_store
    from system.orchestrator import Orchestrator
    from agents.research_agent import ResearchAgent
    from agents.analysis_agent import AnalysisAgent
    from agents.report_agent import ReportAgent

    llm    = create_llm()
    memory = create_memory_store()

    ar = AgentRegistry()
    ar.register(ResearchAgent(llm=llm))   # ← add new agents here
    ar.register(AnalysisAgent(llm=llm))
    ar.register(ReportAgent(llm=llm))

    tr = ToolRegistry()

    return Orchestrator(ar, tr, memory), ar


def run_native(task: str, agent_name: str):
    print(f"\n🚀 Native run  agent: {agent_name}\n   task: {task}\n")
    orch, _ = build_system()

    if agent_name == "pipeline":
        results = orch.run_pipeline(task, ["research_agent","analysis_agent","report_agent"])
        names   = ["research_agent","analysis_agent","report_agent"]
        for i, r in enumerate(results):
            print(f"{'✅' if r.success else '❌'} [{names[i]}]")
            if r.success: print(f"   {r.output[:200]}...")
    else:
        r = orch.run(task=task, agent_name=agent_name)
        print(f"{'✅' if r.success else '❌'} {r.output if r.success else r.error}")

    s = orch.get_trace_summary()
    print(f"\n📊 run_id:{s['run_id'][:8]}  steps:{s['total_steps']}  success_rate:{s['success_rate']}  time:{s['total_latency_ms']:.0f}ms\n")


def run_langgraph(task: str):
    print(f"\n🔗 LangGraph run\n")
    try:
        from adapters.langgraph.graph import build_research_graph
        from langchain_core.messages import HumanMessage
        r = build_research_graph().invoke({"messages": [HumanMessage(content=task)]})
        print(f"✅ {r['messages'][-1].content}")
    except ImportError as e:
        print(f"❌ {e}\n   pip install 'my-agent-project[langgraph]'")


def run_crewai(task: str):
    print(f"\n👥 CrewAI run\n")
    try:
        from adapters.crewai.crew import build_research_crew
        print(build_research_crew().kickoff(inputs={"topic": task}))
    except ImportError as e:
        print(f"❌ {e}\n   pip install 'my-agent-project[crewai]'")


def run_eval():
    from tests.evals.eval_research_agent import run_eval as do_eval, EVAL_CASES
    from agents.research_agent import ResearchAgent
    from core.llm.openai_llm import create_llm
    report = do_eval(ResearchAgent(llm=create_llm()), EVAL_CASES)
    print(f"\n{'='*50}\n  Quality Eval  {report['overall_score']:.1%}  {report['status']}\n{'='*50}")
    for c in report["case_results"]:
        bar = "█"*int(c["score"]*10)+"░"*(10-int(c["score"]*10))
        print(f"  [{bar}] {c['score']:.0%}  {c['description']}")
    print(f"{'='*50}\n")
    return 0 if report["passed"] else 1


def main():
    p = argparse.ArgumentParser(description="my-agent-project", formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("task",        nargs="?", default="")
    p.add_argument("--agent",     default="research_agent", choices=["research_agent","analysis_agent","report_agent","pipeline"])
    p.add_argument("--framework", default="native",         choices=["native","langgraph","crewai"])
    p.add_argument("--eval",      action="store_true")
    p.add_argument("--mcp",       action="store_true")
    args = p.parse_args()

    if args.eval:
        sys.exit(run_eval())
    if args.mcp:
        from protocols.mcp.server import start_mcp_server
        start_mcp_server(port=int(os.environ.get("MCP_SERVER_PORT","8080")))
        return
    if not args.task:
        p.print_help(); return

    {"langgraph": run_langgraph, "crewai": run_crewai}.get(
        args.framework, lambda t: run_native(t, args.agent)
    )(args.task)


if __name__ == "__main__":
    main()
