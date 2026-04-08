"""
Callback Handler - Captures agent events for SSE streaming.
"""
import asyncio
import threading
from typing import Any, Dict, List

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult


class AgentCallbackHandler:
    """
    Callback handler that captures thought/call events for SSE streaming.
    Works with both sync and async contexts.
    """

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._stopped = False
        self._loop: asyncio.AbstractEventLoop = None
        self._thread_lock = threading.Lock()

    def stop(self):
        """Signal the handler to stop."""
        self._stopped = True
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.call_soon_threadsafe(lambda: self._queue.put_nowait(None))
        except:
            pass

    async def _put_event(self, event: Dict[str, Any]):
        """Put event into queue asynchronously."""
        if not self._stopped:
            await self._queue.put(event)

    def _ensure_loop(self):
        """Ensure we have a reference to the event loop."""
        try:
            self._loop = asyncio.get_event_loop()
        except:
            pass

    def on_thought(self, content: str) -> None:
        """Called when agent is thinking."""
        self._ensure_loop()
        if self._loop and not self._stopped:
            try:
                asyncio.run_coroutine_threadsafe(
                    self._put_event({"type": "thought", "content": content}),
                    self._loop
                )
            except:
                pass

    def on_tool_call(self, tool_name: str, args: Dict[str, Any], result: str) -> None:
        """Called when a tool is executed."""
        self._ensure_loop()
        if self._loop and not self._stopped:
            try:
                asyncio.run_coroutine_threadsafe(
                    self._put_event({
                        "type": "call",
                        "tool": tool_name,
                        "args": args,
                        "result": result
                    }),
                    self._loop
                )
            except:
                pass

    async def stream(self):
        """Async generator that yields events."""
        while not self._stopped:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                if event is None:
                    break
                yield event
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
