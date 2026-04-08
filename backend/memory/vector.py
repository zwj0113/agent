"""
Vector Memory Interface - For future Qdrant/Milvus integration.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any


class VectorMemoryInterface(ABC):
    """
    Abstract interface for vector-based long-term memory.
    Used for semantic search over conversation history.
    """

    @abstractmethod
    async def add(self, text: str, metadata: Optional[dict] = None) -> str:
        """
        Add text to the vector store.

        Args:
            text: Text content to store
            metadata: Optional metadata (session_id, timestamp, etc.)

        Returns:
            ID of the stored document
        """
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Search for similar texts.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of search results with text and similarity scores
        """
        pass

    @abstractmethod
    async def delete(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored documents."""
        pass
