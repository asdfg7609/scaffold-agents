"""
system/tracer.py

Observability-First: traces all LLM and tool calls with a run_id.
"""
import uuid
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, TypeVar
from core.utils.logger import get_logger

logger = get_logger(__name__)
T = TypeVar("T")


@dataclass
class TraceEvent:
    run_id:         str
    step:           str
    event_type:     str        # "llm_call" | "tool_call" | "agent_call"
    success:        bool       = True
    error:          str        = ""
    latency_ms:     float      = 0.0
    tokens_used:    int        = 0
    timestamp:      datetime   = field(default_factory=datetime.now)
    metadata:       dict       = field(default_factory=dict)


class Tracer:
    def __init__(self):
        self.run_id   = str(uuid.uuid4())
        self._events: list[TraceEvent] = []
        logger.info(f"[Tracer] Run started: run_id={self.run_id}")

    def record(self, event: TraceEvent) -> None:
        event.run_id = self.run_id
        self._events.append(event)
        icon = "✅" if event.success else "❌"
        logger.info(f"[{self.run_id[:8]}] {icon} {event.step} ({event.event_type}) {event.latency_ms:.0f}ms")
        if not event.success:
            logger.error(f"[{self.run_id[:8]}] Error: {event.error}")

    def timed_call(self, step: str, event_type: str, fn: Callable[[], T], **meta) -> T:
        """Execute a function while measuring elapsed time and recording the result."""
        start = time.time()
        try:
            result = fn()
            self.record(TraceEvent(
                run_id=self.run_id, step=step, event_type=event_type,
                success=True, latency_ms=(time.time()-start)*1000, metadata=meta,
            ))
            return result
        except Exception as e:
            self.record(TraceEvent(
                run_id=self.run_id, step=step, event_type=event_type,
                success=False, error=str(e), latency_ms=(time.time()-start)*1000, metadata=meta,
            ))
            raise

    def get_summary(self) -> dict:
        total   = len(self._events)
        failed  = sum(1 for e in self._events if not e.success)
        total_ms = sum(e.latency_ms for e in self._events)
        return {
            "run_id":           self.run_id,
            "total_steps":      total,
            "failed_steps":     failed,
            "success_rate":     f"{(total-failed)/total*100:.1f}%" if total else "0%",
            "total_latency_ms": round(total_ms, 1),
            "events":           [e.__dict__ for e in self._events],
        }
