"""
AI Agent MVP - FastAPI Backend
"""
import asyncio
import json
import uuid
import queue
import threading
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette import EventSourceResponse

from agents.react import create_react_agent, AgentCallbacks
from memory.history import ChatSession
from tools.registry import ToolRegistry

# Global instances
tool_registry = ToolRegistry()
sessions: Dict[str, ChatSession] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup, cleanup on shutdown."""
    from tools.builtin import CalculatorTool, WeatherTool, DiskUsageTool
    from tools.shell import BashTool
    tool_registry.register(CalculatorTool())
    tool_registry.register(WeatherTool())
    tool_registry.register(DiskUsageTool())
    tool_registry.register(BashTool())
    yield


app = FastAPI(
    title="AI Agent MVP API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID")


class HealthResponse(BaseModel):
    status: str = "ok"


class SkillConfig(BaseModel):
    name: str
    description: str
    tools: List[dict]


@app.get("/api/v1/health")
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/v1/skills")
async def list_skills():
    return {
        "skills": [
            {"name": tool.name, "description": tool.description}
            for tool in tool_registry.list_tools()
        ]
    }


@app.post("/api/v1/skills/install")
async def install_skill(config: SkillConfig):
    return {"status": "installed", "name": config.name}


@app.delete("/api/v1/skills/{name}")
async def uninstall_skill(name: str):
    return {"status": "uninstalled", "name": name}


@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE endpoint for streaming chat responses."""
    session_id = request.session_id or str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = ChatSession(session_id)
    chat_session = sessions[session_id]

    chat_session.add_user_message(request.message)
    chat_history = chat_session.get_messages_for_context()

    # Create agent
    agent = create_react_agent(
        tools=list(tool_registry.list_tools()),
        callbacks=None,
    )

    # Queue for events between threads
    event_queue: queue.Queue = queue.Queue()
    full_answer = [""]

    def agent_thread():
        """Run agent in background thread, put events in queue."""
        try:
            for event in agent.invoke_streaming(request.message, chat_history):
                event_queue.put(event)
            event_queue.put(None)  # Sentinel to signal completion
        except Exception as e:
            print(f"[ERROR in agent_thread] {str(e)}")
            event_queue.put({"type": "error", "content": str(e)})
            event_queue.put(None)

    async def event_generator() -> AsyncGenerator[dict, None]:
        nonlocal full_answer

        # Start agent in background thread
        thread = threading.Thread(target=agent_thread, daemon=True)
        thread.start()

        try:
            while True:
                # Get event from queue with timeout
                try:
                    event = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: event_queue.get(timeout=120)
                    )
                except queue.Empty:
                    yield {
                        "event": "message",
                        "data": json.dumps({"type": "error", "content": "Timeout waiting for response"}),
                    }
                    break

                if event is None:  # Agent finished
                    break

                yield {
                    "event": "message",
                    "data": json.dumps(event),
                }

                if event.get("type") == "answer":
                    full_answer[0] = event.get("content", "")

        except Exception as e:
            print(f"[ERROR in event_generator] {str(e)}")
            yield {
                "event": "message",
                "data": json.dumps({"type": "error", "content": str(e)}),
            }
        finally:
            thread.join(timeout=5)
            if full_answer[0]:
                chat_session.add_ai_message(full_answer[0])

    return EventSourceResponse(event_generator())
