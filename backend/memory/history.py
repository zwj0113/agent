"""
Chat Session Memory - In-memory session history management.
"""
from typing import List, Dict

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class ChatSession:
    """Manages chat history for a single session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._messages: List[BaseMessage] = []

    def add_user_message(self, content: str) -> None:
        """Add a user message to the session."""
        self._messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str) -> None:
        """Add an AI message to the session."""
        self._messages.append(AIMessage(content=content))

    def get_history(self) -> BaseChatMessageHistory:
        """Get the chat history as a LangChain message history."""
        return InMemoryChatHistory(messages=self._messages)

    def get_messages_for_context(self) -> List[Dict[str, str]]:
        """
        Get messages in a simple dict format for the API.
        Returns list of {'role': 'user'/'assistant', 'content': ...}
        """
        messages = []
        for msg in self._messages:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content})
        return messages


class InMemoryChatHistory(BaseChatMessageHistory):
    """In-memory implementation of BaseChatMessageHistory."""

    def __init__(self, messages: List[BaseMessage] = None):
        self._messages = messages or []

    @property
    def messages(self) -> List[BaseMessage]:
        """Return message history."""
        return self._messages

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add messages to the history."""
        self._messages.extend(messages)

    def clear(self) -> None:
        """Clear the message history."""
        self._messages = []
