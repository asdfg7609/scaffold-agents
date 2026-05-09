"""
core/llm/openai_llm.py — OpenAI GPT implementation + LLM factory
Same interface as ClaudeLLM → swap without changing orchestrator code (LSP).
"""
import os
from core.llm.base_llm import BaseLLM, LLMResponse


class OpenAILLM(BaseLLM):
    def __init__(self, model: str | None = None):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("pip install openai")
        self.model = model or "gpt-4o"

    def chat(self, messages, system="", max_tokens=4096, tools=None) -> LLMResponse:
        full = []
        if system:
            full.append({"role": "system", "content": system})
        full.extend(messages)
        kwargs = {"model": self.model, "max_tokens": max_tokens, "messages": full}
        if tools:
            kwargs["tools"] = tools
        r = self.client.chat.completions.create(**kwargs)
        return LLMResponse(
            content=r.choices[0].message.content or "",
            input_tokens=r.usage.prompt_tokens,
            output_tokens=r.usage.completion_tokens,
            model=self.model,
        )

    def get_model_name(self) -> str:
        return self.model


def create_llm(provider: str | None = None) -> BaseLLM:
    """Environment-variable-based LLM factory (DIP — orchestrator calls only this)."""
    provider = provider or os.environ.get("DEFAULT_LLM_PROVIDER", "claude")
    if provider == "openai":
        return OpenAILLM()
    from core.llm.claude_llm import ClaudeLLM
    return ClaudeLLM()
