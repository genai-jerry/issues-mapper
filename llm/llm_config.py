"""
LLM Configuration Module

Handles configuration for LLM providers and models.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """Configuration for LLM providers and models."""
    
    # Embedding configuration
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-ada-002"
    embedding_api_key: Optional[str] = None
    
    # Chat configuration
    chat_provider: str = "openai"
    chat_model: str = "gpt-3.5-turbo"
    chat_api_key: Optional[str] = None
    
    # OpenRouter configuration
    openrouter_api_key: Optional[str] = None
    
    # Cache configuration
    enable_cache: bool = True
    cache_dir: str = ".llm_cache"
    
    def __post_init__(self):
        """Load configuration from file if available."""
        if os.path.exists("llm_config.json"):
            self.load_from_file("llm_config.json")
    
    def load_from_file(self, filepath: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except Exception as e:
            print(f"Warning: Could not load config from {filepath}: {e}")
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        config_data = {
            'embedding_provider': self.embedding_provider,
            'embedding_model': self.embedding_model,
            'embedding_api_key': self.embedding_api_key,
            'chat_provider': self.chat_provider,
            'chat_model': self.chat_model,
            'chat_api_key': self.chat_api_key,
            'openrouter_api_key': self.openrouter_api_key,
            'enable_cache': self.enable_cache,
            'cache_dir': self.cache_dir
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration."""
        api_key = self.embedding_api_key
        if self.embedding_provider == "openrouter":
            api_key = self.openrouter_api_key
        
        return {
            "provider": self.embedding_provider,
            "model": self.embedding_model,
            "api_key": api_key
        }
    
    def get_chat_config(self) -> Dict[str, Any]:
        """Get chat configuration."""
        api_key = self.chat_api_key
        if self.chat_provider == "openrouter":
            api_key = self.openrouter_api_key
        
        return {
            "provider": self.chat_provider,
            "model": self.chat_model,
            "api_key": api_key,
            "temperature": 0.7,
            "max_tokens": 1000
        }
    
    def set_embedding_config(self, provider: str, model: str, api_key: str = None):
        """Set embedding configuration."""
        self.embedding_provider = provider
        self.embedding_model = model
        if api_key:
            self.embedding_api_key = api_key
    
    def set_chat_config(self, provider: str, model: str, api_key: str = None):
        """Set chat configuration."""
        self.chat_provider = provider
        self.chat_model = model
        if api_key:
            self.chat_api_key = api_key
    
    def set_openrouter_config(self, api_key: str):
        """Set OpenRouter configuration."""
        self.openrouter_api_key = api_key


# Global configuration instance
config = LLMConfig() 