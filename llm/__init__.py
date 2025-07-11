"""
LLM package for language model interactions.

This package contains all LLM-related functionality including:
- Chat model management
- Text generation
- Code analysis
- Model configuration
"""

from .llm_manager import LLMManager
from .llm_config import LLMConfig

__all__ = [
    'LLMManager',
    'LLMConfig',
] 