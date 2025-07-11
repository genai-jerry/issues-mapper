"""
Embeddings package for code module embedding functionality.

This package contains all embedding-related functionality including:
- Embedding generation and management
- Embedding utilities and helpers
- Embedding configuration
"""

from .embedding_manager import EmbeddingManager
from .embedding_utils import *
from .embedding_config import EmbeddingConfig

__all__ = [
    'EmbeddingManager',
    'EmbeddingConfig',
] 