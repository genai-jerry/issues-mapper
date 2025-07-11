"""
Vector Models Module

Defines data models for vector storage operations.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List


@dataclass
class VectorDocument:
    """Represents a document with vector embedding."""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorDocument':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            embedding=data["embedding"],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )


@dataclass
class VectorSearchResult:
    """Represents a search result with similarity score."""
    document: VectorDocument
    score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document": self.document.to_dict(),
            "score": self.score
        }


@dataclass
class CollectionStats:
    """Statistics for a vector collection."""
    name: str
    document_count: int
    embedding_dimension: int
    created_at: datetime
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "document_count": self.document_count,
            "embedding_dimension": self.embedding_dimension,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        } 