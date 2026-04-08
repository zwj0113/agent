"""
ReAct Agent - Implements ReAct loop with MiniMax API and tool execution.
Supports streaming LLM responses in real-time.
"""
import os
import json
import re
import html
import threading
from typing import List, Optional, Dict, Any, Generator

import requests
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

# MiniMax configuration
DEFAULT_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com")


class AgentCallbacks:
    """Simple thread-safe event collector for agent events."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def add_event(self, event_type: str, data: Dict[str, Any]):
        with self.lock:
            self.events.append({"type": event_type, **data})

    def get_events(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.events)

    def clear(self):
        with self.lock:
            self.events.clear()


def clean_thinking_tags(text: str) -> str:
    """Remove thinking tags from text."""
    text = html.unescape(text)
    text = re.sub(r'<\|im_start\|>.*?<\|im_end\|>', '', text, flags=re.DOTALL)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()


class ReActAgent:
    """
    ReAct (Reasoning + Acting) agent implementation.
    Uses MiniMax API for reasoning and executes tools when needed.
    Supports streaming LLM responses.
    """

    def __init__(self, tools: List[BaseTool], callbacks: Optional[AgentCallbacks] = None):
        self.tools = {tool.name: tool for tool in tools}
        self.callbacks = callbacks

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call MiniMax API and return the full response."""
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "stream": False,
        }

        response = requests.post(
            f"{MINIMAX_BASE_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _call_llm_streaming(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Call MiniMax API with streaming and yield chunks."""
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "stream": True,
        }

        response = requests.post(
            f"{MINIMAX_BASE_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
            stream=True,
        )

        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

        for line in response.iter_lines():
            if not line:
                continue

            line = line.decode('utf-8', errors='replace')

            if line.startswith("data: "):
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content_chunk = delta.get("content", "")

                    if content_chunk:
                        yield content_chunk

                except json.JSONDecodeError:
                    continue

    def _build_system_prompt(self) -> str:
        """Build the system prompt with available tools."""
        tools_desc = []
        for name, tool in self.tools.items():
            tools_desc.append(f"- **{name}**: {tool.description}")

        tools_list = "\n".join(tools_desc)

        return f"""You are an expert AI assistant that can use tools to complete complex tasks.

You have access to these tools:
{tools_list}

## IMPORTANT: How to use tools

When you need to use a tool, respond with this EXACT format:

```
Action: tool_name
Action Input: the_input_value
```

After sending a tool request, you will receive the tool's result. Then continue reasoning!

## Task Completion Process:

1. First, reason about what the user is asking
2. If you need to use a tool, use it
3. After getting the tool result, CONTINUE your reasoning
4. If more steps are needed, use more tools
5. Only give the final answer when the task is truly complete

## Examples:

**Example 1 - Multi-step calculation:**
User: What is 100 + 200 + 300?
You: Let me calculate this step by step.
```
Action: calculator
Action Input: 100 + 200
```
(Tool result: 300)

You: Good, first step is 300. Now I need to add 300.
```
Action: calculator
Action Input: 300 + 300
```
(Tool result: 600)

You: 100 + 200 + 300 = 600

**Example 2 - Download task:**
User: Download this video from example.com
You: I need to use a download tool for this.
```
Action: bash
Action Input: youtube-dl "https://example.com/video"
```
(Tool result: Downloading... 100%)

You: The download completed successfully.

## Rules:
1. ALWAYS use the exact format shown above for tool calls
2. After getting a tool result, continue your reasoning
3. If you need multiple tools, use them in sequence
4. Be thorough - don't stop until the task is complete
5. Present your final answer clearly"""

    def _parse_action(self, text: str) -> Optional[tuple]:
        """Parse action and action input from LLM response."""
        action_match = re.search(r'Action:\s*(\w+)', text, re.IGNORECASE)
        input_match = re.search(r'Action Input:\s*(.+)', text, re.IGNORECASE | re.DOTALL)

        if action_match:
            tool_name = action_match.group(1).strip()
            action_input = input_match.group(1).strip() if input_match else ""
            action_input = action_input.strip().strip('"\'')
            action_input = re.split(r'\n|`', action_input)[0].strip()
            return tool_name, action_input

        return None

    def _execute_tool(self, tool_name: str, action_input: str) -> str:
        """Execute a tool and return the result."""
        if tool_name not in self.tools:
            available = ", ".join(self.tools.keys())
            return f"Error: Tool '{tool_name}' not found. Available tools: {available}"

        tool = self.tools[tool_name]
        try:
            result = tool.invoke(action_input)
            return str(result)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def invoke(self, message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Process a message using ReAct loop (non-streaming version)."""
        if self.callbacks:
            self.callbacks.clear()

        system_msg = {"role": "system", "content": self._build_system_prompt()}

        history_context = ""
        if chat_history:
            history_parts = []
            for msg in chat_history[-8:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    history_parts.append(f"User: {content}")
                else:
                    history_parts.append(f"Assistant: {content}")
            history_context = "\n".join(history_parts)

        if history_context:
            user_msg = {
                "role": "user",
                "content": f"Conversation history:\n{history_context}\n\nCurrent task: {message}"
            }
        else:
            user_msg = {"role": "user", "content": message}

        messages = [system_msg, user_msg]

        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            llm_response = self._call_llm(messages)

            # Extract and record thought content (before Action block)
            action_match = re.search(r'Action:\s*(\w+)', llm_response, re.IGNORECASE)
            if action_match:
                thought_content = llm_response[:action_match.start()].strip()
                thought_content = clean_thinking_tags(thought_content)
                if thought_content and self.callbacks:
                    self.callbacks.add_event("thought", {"content": thought_content})
            else:
                # No action block - check for thinking tags
                thought_content = clean_thinking_tags(llm_response)
                if thought_content and self.callbacks:
                    self.callbacks.add_event("thought", {"content": thought_content})

            action = self._parse_action(llm_response)

            if action:
                tool_name, action_input = action

                tool_result = self._execute_tool(tool_name, action_input)

                if self.callbacks:
                    self.callbacks.add_event("call", {
                        "tool": tool_name,
                        "args": {"input": action_input},
                        "result": tool_result
                    })

                messages.append({"role": "assistant", "content": llm_response})
                messages.append({"role": "user", "content": f"Tool result: {tool_result}\n\nContinue your reasoning and provide the final answer if the task is complete, or use another tool if needed."})
            else:
                # Return cleaned answer without thinking tags
                clean_answer = clean_thinking_tags(llm_response)
                return {"output": clean_answer}

        return {"output": "I tried multiple approaches but couldn't complete this task. Please try rephrasing your request."}

    def invoke_streaming(self, message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Generator[Dict[str, Any], None, None]:
        """
        Process a message using ReAct loop with streaming.
        Yields events as they happen.
        """
        if self.callbacks:
            self.callbacks.clear()

        system_msg = {"role": "system", "content": self._build_system_prompt()}

        history_context = ""
        if chat_history:
            history_parts = []
            for msg in chat_history[-8:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    history_parts.append(f"User: {content}")
                else:
                    history_parts.append(f"Assistant: {content}")
            history_context = "\n".join(history_parts)

        if history_context:
            user_msg = {
                "role": "user",
                "content": f"Conversation history:\n{history_context}\n\nCurrent task: {message}"
            }
        else:
            user_msg = {"role": "user", "content": message}

        messages = [system_msg, user_msg]

        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Collect streaming content from LLM
            full_content = ""
            found_action = False
            thought_emitted = False

            for chunk in self._call_llm_streaming(messages):
                full_content += chunk

                # Check if we've hit an Action block
                if not found_action:
                    action_match = re.search(r'Action:\s*(\w+)', full_content, re.IGNORECASE)
                    if action_match:
                        found_action = True
                        # Extract thought content (before Action block)
                        thought_part = full_content[:action_match.start()].strip()
                        thought_part = clean_thinking_tags(thought_part)
                        if thought_part:
                            yield {"type": "thought", "content": thought_part}
                            thought_emitted = True

            # Process the full LLM response
            if not found_action:
                # No action block - this is a final answer
                clean_answer = clean_thinking_tags(full_content)
                if clean_answer:
                    yield {"type": "answer", "content": clean_answer}
                return

            action = self._parse_action(full_content)

            if action:
                tool_name, action_input = action

                tool_result = self._execute_tool(tool_name, action_input)

                yield {
                    "type": "call",
                    "tool": tool_name,
                    "args": {"input": action_input},
                    "result": tool_result
                }

                messages.append({"role": "assistant", "content": full_content})
                messages.append({"role": "user", "content": f"Tool result: {tool_result}\n\nContinue your reasoning and provide the final answer if the task is complete, or use another tool if needed."})
            else:
                # No action found but we thought we had one - emit remaining as answer
                clean_answer = clean_thinking_tags(full_content)
                if clean_answer:
                    yield {"type": "answer", "content": clean_answer}
                return

        # Max iterations reached
        yield {"type": "answer", "content": "I tried multiple approaches but couldn't complete this task. Please try rephrasing your request."}


def create_react_agent(
    tools: List[BaseTool],
    callbacks: Optional[AgentCallbacks] = None,
    chat_history: Optional[BaseChatMessageHistory] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
) -> ReActAgent:
    """Create a ReAct agent with the given tools."""
    return ReActAgent(tools=tools, callbacks=callbacks)
