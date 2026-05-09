# Contributing to my-agent-project

Thanks for your interest. Contributions are welcome and the bar is intentionally low.

---

## What's Most Needed

The highest-value contributions right now, in priority order:

1. **Framework adapters** — AutoGen, OpenAI Agents SDK, Google ADK
2. **Real tool implementations** — Tavily search, SerpAPI, actual Slack webhook
3. **Tracing integrations** — LangSmith, Langfuse
4. **GitHub Actions CI** — automated test runs on PRs
5. **Bug reports** — open an issue with a minimal reproduction

---

## How to Add a Framework Adapter

This is the most impactful contribution you can make.

The pattern is always the same: wrap `domain/tools/` functions in whatever
decorator the framework requires, then wire up the agent and orchestrator.

### Step 1 — Create the adapter directory

```bash
mkdir adapters/autogen
touch adapters/autogen/__init__.py
touch adapters/autogen/tools.py
touch adapters/autogen/agents.py
```

### Step 2 — Wrap the tools

```python
# adapters/autogen/tools.py
# Import from domain/ only — never from adapters/ or system/

from domain.tools.green.search import search_news
from domain.tools.yellow.write_file import write_file

def get_autogen_tools() -> list:
    # wrap each function in AutoGen's tool format
    ...
```

### Step 3 — Wire up the agents

```python
# adapters/autogen/agents.py
from domain.prompts.researcher import RESEARCHER_SYSTEM_PROMPT
from adapters.autogen.tools import get_autogen_tools

def build_research_agent():
    ...
```

### Step 4 — Add to main.py

Add a `run_autogen(task)` function and a `--framework autogen` option.

### Step 5 — Add an integration test

```python
# tests/integration/test_autogen.py
def test_autogen_research_agent():
    ...
```

---

## Rules for Contributions

**domain/ must stay framework-free**

No `langchain`, `crewai`, `autogen`, or `pydantic_ai` imports inside `domain/`.
This is the non-negotiable constraint that makes the whole architecture work.

```python
# domain/tools/green/my_tool.py

# ✅ allowed
import os
import requests
from pydantic import BaseModel

# ❌ not allowed
from langchain_core.tools import tool
from crewai.tools import BaseTool
```

**One tool, one action**

Tools must be atomic. If your tool does two things, split it into two tools.

```python
# ❌ too broad
def manage_files(action: str, path: str, content: str = ""): ...

# ✅ correct
def read_file(path: str) -> dict: ...
def write_file(path: str, content: str) -> dict: ...
```

**Classify reversibility**

Every tool must be placed in the correct folder:

- `domain/tools/green/` — read-only, safe to retry
- `domain/tools/yellow/` — creates or modifies state, include idempotency key
- `domain/tools/red/` — sends, deletes, pays — requires human approval

**Tests must pass without API keys**

`pytest tests/unit/ -v` must pass on a machine with no `.env` file.
Use `MockLLM` from `tests/unit/test_system.py` for any tests that involve LLMs.

---

## Pull Request Checklist

Before opening a PR:

- [ ] `pytest tests/unit/ -v` passes locally
- [ ] No framework imports inside `domain/`
- [ ] New tools are placed in the correct green/yellow/red folder
- [ ] PR description explains what changed and why

---

## Opening Issues

For bugs: include the exact command you ran and the full error output.

For feature requests: explain the use case, not just the feature.

---

## Questions

Open a GitHub Discussion or an issue labeled `question`.
