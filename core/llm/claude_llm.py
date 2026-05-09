"""
core/llm/claude_llm.py — Anthropic Claude implementation
"""
import os
from core.llm.base_llm import BaseLLM, LLMResponse


class ClaudeLLM(BaseLLM):
    def __init__(self, model: str | None = None):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        except ImportError:
            raise ImportError("pip install anthropic")
        self.model = model or os.environ.get("DEFAULT_MODEL", "claude-opus-4-5")

    def chat(self, messages, system="", max_tokens=4096, tools=None) -> LLMResponse:
        kwargs = {"model": self.model, "max_tokens": max_tokens, "messages": messages}
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools
        r = self.client.messages.create(**kwargs)
        return LLMResponse(
            content=r.content[0].text if r.content else "",
            input_tokens=r.usage.input_tokens,
            output_tokens=r.usage.output_tokens,
            model=self.model,
        )

    def get_model_name(self) -> str:
        return self.model
