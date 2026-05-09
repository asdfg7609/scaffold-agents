"""
tests/evals/eval_research_agent.py

Agent quality evaluation (score-based).
Used as a score-threshold deployment gate in CI/CD.
"""
import os
from dataclasses import dataclass
from typing import Callable


@dataclass
class EvalCase:
    input:       str
    evaluator:   Callable[[str], float]
    description: str
    weight:      float = 1.0


def keyword_coverage(output: str, keywords: list[str]) -> float:
    if not output: return 0.0
    return sum(1 for k in keywords if k.lower() in output.lower()) / len(keywords)


def length_score(output: str, mn: int, mx: int) -> float:
    n = len(output)
    if n < mn: return n / mn
    if n > mx: return mx / n
    return 1.0


EVAL_CASES = [
    EvalCase("Research LangGraph",              lambda o: keyword_coverage(o, ["LangGraph","state","graph","node"]),       "LangGraph keywords", weight=1.5),
    EvalCase("Latest AI agent trends",          lambda o: keyword_coverage(o, ["agent","AI","2025","framework"]),          "Trend keywords",     weight=1.0),
    EvalCase("Python async programming",        lambda o: length_score(o, 100, 2000),                                      "Response length",    weight=0.8),
]


def run_eval(agent, cases=EVAL_CASES) -> dict:
    threshold    = float(os.environ.get("EVAL_PASS_THRESHOLD", "0.7"))
    results      = []
    total_weight = sum(c.weight for c in cases)
    weighted     = 0.0

    for case in cases:
        try:
            r     = agent.run(input=case.input)
            score = case.evaluator(r.output) if r.success else 0.0
            ok    = r.success
        except Exception:
            score, ok = 0.0, False

        weighted += score * case.weight
        results.append({"description": case.description, "score": round(score,3), "weight": case.weight, "success": ok})

    overall = weighted / total_weight if total_weight else 0.0
    passed  = overall >= threshold
    return {
        "overall_score": round(overall,3),
        "threshold":     threshold,
        "passed":        passed,
        "status":        "✅ PASS" if passed else "❌ FAIL",
        "case_results":  results,
    }


if __name__ == "__main__":
    from agents.research_agent import ResearchAgent
    from tests.unit.test_system import MockLLM

    agent  = ResearchAgent(llm=MockLLM("LangGraph is a state-based AI agent graph framework."))
    report = run_eval(agent)

    print(f"\n{'='*50}\n  Agent Quality Evaluation\n{'='*50}")
    print(f"  Overall Score: {report['overall_score']:.1%}  {report['status']}")
    for c in report["case_results"]:
        bar = "█"*int(c["score"]*10) + "░"*(10-int(c["score"]*10))
        print(f"    [{bar}] {c['score']:.0%}  {c['description']}")
    print(f"{'='*50}\n")
