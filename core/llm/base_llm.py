"""
core/llm/base_llm.py

LLM adapter layer — guarantees LSP.
Swapping Claude → GPT → local model does not change orchestrator code.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM response — common return type for all implementations"""
    content:       str
    input_tokens:  int
    output_tokens: int
    model:         str


class BaseLLM(ABC):
    """Common interface for LLMs."""

    @abstractmethod
    def chat(
        self,
        messages:   list[dict],
        system:     str = "",
        max_tokens: int = 4096,
        tools:      list[dict] | None = None,
    ) -> LLMResponse:
        """Send messages to the LLM and receive a response."""
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """Name of the currently active model."""
        ...
