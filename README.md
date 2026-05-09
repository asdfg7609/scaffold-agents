# my-agent-project

> Switch between LangGraph, CrewAI, and Pydantic AI **without rewriting your business logic.**
> 90% of your code stays the same when you change frameworks or models.

**26 tests pass with zero API keys.**

---

```bash
git clone https://github.com/your-username/my-agent-project
cd my-agent-project
pip install -e ".[dev]"
pytest tests/unit/ -v          # ✅ 26 passed — no API key needed
cp .env.example .env           # add your API key, then:
python main.py "Research the latest trends in AI agents"
```

---

## The Problem This Solves

Most AI agent tutorials look like this:

```python
# research_agent.py
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

llm = ChatAnthropic(model="claude-opus-4-5")

@tool
def search(query: str) -> str: ...

agent = llm.bind_tools([search])
```

This works for demos. It breaks in production because:

- **Framework lock-in** — switching from LangGraph to CrewAI means rewriting everything
- **Model lock-in** — swapping Claude for GPT requires touching every file that calls the LLM
- **Untestable** — you need a real API key just to run a test
- **No safety rails** — nothing stops the agent from sending emails without approval
- **No observability** — when it fails, you don't know where or why

This project is the architecture you build *before* the agent logic goes in.

---

## How It Works

The core idea: **separate what changes from what stays the same.**

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: System  (trust boundaries, guardrails, tracing)   │  ← changes with security policy
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Tools   (search, file ops, notifications)         │  ← changes with external APIs
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Memory  (session state, short/long-term memory)   │  ← changes with session policy
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Core    (interfaces, LLM adapters, registries)    │  ← changes with LLM or framework
└─────────────────────────────────────────────────────────────┘
```

When you swap LangGraph for CrewAI, only `adapters/` changes.
When you swap Claude for GPT, only `core/llm/openai_llm.py` changes.
Your business logic — tools, prompts, schemas — never changes.

---

## What You Get

### Framework-agnostic by design

The same domain logic runs on three different frameworks:

```bash
python main.py "Research AI agents"                    # Native (no framework)
python main.py "Research AI agents" --framework langgraph
python main.py "Research AI agents" --framework crewai
```

### Tests that don't need an API key

```python
class MockLLM(BaseLLM):
    def chat(self, messages, **kwargs) -> LLMResponse:
        return LLMResponse(content="Mock response", ...)

# Test the full orchestrator pipeline — zero API calls
def test_pipeline_stops_on_failure():
    orch = Orchestrator(registry, tools, memory)
    results = orch.run_pipeline("input", ["research_agent", "analysis_agent"])
    assert results[0].success is False  # passes instantly
```

### Built-in safety rails

Every tool is classified by reversibility. Irreversible actions require human approval:

```
GREEN  → auto-execute    (read_file, search_news)
YELLOW → audit log       (write_file, update_record)
RED    → human approval  (send_email, delete_data, process_payment)
```

RED tools are blocked without explicit approval — enforced at the infrastructure
level, not just in the prompt.

### Full execution tracing

Every LLM call and tool invocation is tracked with a `run_id`:

```
[a3f9c12b] ✅ research_agent  (agent_call)  1243ms
[a3f9c12b] ✅ search_news     (tool_call)    312ms
[a3f9c12b] ✅ analysis_agent  (agent_call)   987ms
[a3f9c12b] ❌ write_file      (tool_call)     45ms  ERROR: path traversal blocked
```

---

## Project Structure

```
my-agent-project/
│
├── AGENTS.md                    ← shared rules injected into every agent (DRY)
│
├── core/                        ← framework-agnostic infrastructure
│   ├── interfaces/              ← BaseAgent, BaseTool, BaseMemory (DIP)
│   ├── llm/                     ← LLM adapters: Claude, OpenAI (LSP)
│   ├── registry/                ← ToolRegistry, AgentRegistry (OCP)
│   └── utils/                   ← retry logic, logger (DRY)
│
├── domain/                      ← pure business logic — no framework imports
│   ├── tools/
│   │   ├── green/               ← reversible: search, read
│   │   ├── yellow/              ← partially reversible: write, update
│   │   └── red/                 ← irreversible: notify, delete, pay
│   ├── prompts/                 ← system prompts (one per agent role)
│   └── schemas/                 ← Pydantic I/O types
│
├── memory/                      ← session state management
│   ├── in_memory_store.py       ← development backend
│   └── redis_store.py           ← production backend (drop-in swap)
│
├── system/                      ← guardrails and observability
│   ├── orchestrator.py          ← runs agents, manages state
│   ├── reversibility_guard.py   ← GREEN / YELLOW / RED gate
│   ├── trust_boundary.py        ← prompt injection defense
│   ├── hitl.py                  ← human-in-the-loop approval
│   └── tracer.py                ← run_id tracing, audit log
│
├── adapters/                    ← the ONLY part that changes per framework
│   ├── langgraph/               ← wraps domain/tools with @tool + StateGraph
│   ├── crewai/                  ← wraps domain/tools with BaseTool + Crew
│   └── pydantic_ai/             ← wraps domain/tools with @agent.tool
│
├── agents/                      ← concrete implementations (one role each)
│   ├── research_agent.py
│   ├── analysis_agent.py
│   └── report_agent.py
│
├── protocols/                   ← expose agents to external systems
│   ├── mcp/server.py            ← serve tools over MCP (Anthropic standard)
│   └── a2a/agent_card.py        ← A2A agent discovery (Google standard)
│
└── tests/
    ├── unit/                    ← 26 tests, no API key needed
    ├── integration/             ← uses real LLM if API key is present
    └── evals/                   ← score-based quality evaluation
```

---

## Design Principles

This project applies SOLID principles to AI agent code — adapted for
the non-deterministic nature of LLMs.

| Principle | Applied here |
|---|---|
| **SRP** | One agent, one role. One tool, one action. |
| **OCP** | Add tools via registry — no if-else chains in the orchestrator |
| **LSP** | Swap Claude for GPT — tests still pass |
| **ISP** | Each agent only receives the tools it needs |
| **DIP** | Orchestrator calls `BaseAgent`, not `ClaudeResearchAgent` |
| **DRY** | `AGENTS.md` is the single source of truth for all agent rules |

Three AI-specific principles enforced structurally:

- **Reversibility** — GREEN / YELLOW / RED classification; irreversible actions require human approval
- **Trust Boundary** — untrusted external data is isolated from system instructions to defend against prompt injection
- **Observability-First** — every call is traced with a `run_id` from the start

---

## Quickstart

```bash
# 1. Install
pip install -e ".[dev]"           # core + tests
pip install -e ".[langgraph]"     # + LangGraph adapter
pip install -e ".[crewai]"        # + CrewAI adapter
pip install -e ".[all]"           # everything

# 2. Configure
cp .env.example .env
# edit .env: add ANTHROPIC_API_KEY or OPENAI_API_KEY

# 3. Test (no API key needed)
pytest tests/unit/ -v

# 4. Run
python main.py "What are the latest developments in AI agents?"
python main.py "AI trends" --agent pipeline        # research → analysis → report
python main.py "AI trends" --framework langgraph
python main.py "AI trends" --framework crewai
python main.py --eval                              # quality evaluation
python main.py --mcp                               # start MCP server
```

---

## Adapting This to Your Project

**Adding a new tool**
1. Write a pure Python function in `domain/tools/green/` (or yellow/red)
2. Wrap it in `adapters/{framework}/tools.py`
3. Register it in `main.py`

**Adding a new agent**
1. Create `agents/my_agent.py` extending `BaseAgent`
2. Register it in `main.py`: `registry.register(MyAgent(llm=llm))`

**Switching frameworks** — only `adapters/` changes.

**Switching LLM providers** — implement `BaseLLM`, update the factory in `core/llm/openai_llm.py`.

---

## What's Real vs. Mock

The tools in `domain/tools/` use minimal implementations to keep the
architecture readable. Replace these for production:

| File | Replace with |
|---|---|
| `domain/tools/green/search.py` | [Tavily](https://tavily.com), [SerpAPI](https://serpapi.com), Bing Search API |
| `domain/tools/red/notify.py` | Real Slack webhook |
| `memory/in_memory_store.py` | `redis_store.py` (already included) |

Everything else — interfaces, orchestrator, guardrails, tracing, adapters — is production-ready.

---

## Roadmap

- [ ] AutoGen adapter
- [ ] OpenAI Agents SDK adapter
- [ ] Google ADK adapter
- [ ] LangSmith / Langfuse tracing integration
- [ ] Real search tool examples (Tavily, SerpAPI)
- [ ] GitHub Actions CI workflow

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a framework adapter.

---

## License

MIT
