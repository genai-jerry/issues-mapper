"""
LLM Configuration Module

Handles configuration for LLM providers, models, and API keys.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class LLMConfig:
    """Configuration for LLM providers and models."""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_embedding_model: str = "text-embedding-ada-002"
    openai_chat_model: str = "gpt-3.5-turbo"
    
    # HuggingFace Configuration
    huggingface_api_key: Optional[str] = None
    huggingface_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    huggingface_chat_model: str = "microsoft/DialoGPT-medium"
    
    # Anthropic Configuration
    anthropic_api_key: Optional[str] = None
    anthropic_chat_model: str = "claude-3-sonnet-20240229"
    
    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = None
    openrouter_chat_model: str = "openai/gpt-3.5-turbo"
    openrouter_embedding_model: str = "openai/text-embedding-ada-002"
    
    # General Settings
    default_embedding_provider: str = "openai"
    default_chat_provider: str = "openai"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Cache Settings
    enable_cache: bool = True
    cache_dir: str = ".llm_cache"
    
    def __post_init__(self):
        """Load configuration from environment variables and config files."""
        self._load_from_env()
        self._load_from_config_file()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_EMBEDDING_MODEL"):
            self.openai_embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL")
        if os.getenv("OPENAI_CHAT_MODEL"):
            self.openai_chat_model = os.getenv("OPENAI_CHAT_MODEL")
        
        # HuggingFace
        if os.getenv("HUGGINGFACE_API_KEY"):
            self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        if os.getenv("HUGGINGFACE_EMBEDDING_MODEL"):
            self.huggingface_embedding_model = os.getenv("HUGGINGFACE_EMBEDDING_MODEL")
        if os.getenv("HUGGINGFACE_CHAT_MODEL"):
            self.huggingface_chat_model = os.getenv("HUGGINGFACE_CHAT_MODEL")
        
        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("ANTHROPIC_CHAT_MODEL"):
            self.anthropic_chat_model = os.getenv("ANTHROPIC_CHAT_MODEL")
        
        # OpenRouter
        if os.getenv("OPENROUTER_API_KEY"):
            self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if os.getenv("OPENROUTER_CHAT_MODEL"):
            self.openrouter_chat_model = os.getenv("OPENROUTER_CHAT_MODEL")
        if os.getenv("OPENROUTER_EMBEDDING_MODEL"):
            self.openrouter_embedding_model = os.getenv("OPENROUTER_EMBEDDING_MODEL")
        
        # General settings
        if os.getenv("DEFAULT_EMBEDDING_PROVIDER"):
            self.default_embedding_provider = os.getenv("DEFAULT_EMBEDDING_PROVIDER")
        if os.getenv("DEFAULT_CHAT_PROVIDER"):
            self.default_chat_provider = os.getenv("DEFAULT_CHAT_PROVIDER")
        if os.getenv("LLM_TEMPERATURE"):
            self.temperature = float(os.getenv("LLM_TEMPERATURE"))
        if os.getenv("LLM_MAX_TOKENS"):
            self.max_tokens = int(os.getenv("LLM_MAX_TOKENS"))
    
    def _load_from_config_file(self):
        """Load configuration from config file if it exists."""
        config_paths = [
            Path("llm_config.json"),
            Path.home() / ".llm_config.json",
            Path("config/llm_config.json")
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                    
                    # Update attributes from config file
                    for key, value in config_data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
                    break
                except Exception as e:
                    print(f"Warning: Could not load config from {config_path}: {e}")
    
    def save_config(self, filepath: str = "llm_config.json"):
        """Save current configuration to a JSON file."""
        config_data = {
            "openai_api_key": self.openai_api_key,
            "openai_embedding_model": self.openai_embedding_model,
            "openai_chat_model": self.openai_chat_model,
            "huggingface_api_key": self.huggingface_api_key,
            "huggingface_embedding_model": self.huggingface_embedding_model,
            "huggingface_chat_model": self.huggingface_chat_model,
            "anthropic_api_key": self.anthropic_api_key,
            "anthropic_chat_model": self.anthropic_chat_model,
            "openrouter_api_key": self.openrouter_api_key,
            "openrouter_chat_model": self.openrouter_chat_model,
            "openrouter_embedding_model": self.openrouter_embedding_model,
            "default_embedding_provider": self.default_embedding_provider,
            "default_chat_provider": self.default_chat_provider,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enable_cache": self.enable_cache,
            "cache_dir": self.cache_dir
        }
        
        # Remove None values for security
        config_data = {k: v for k, v in config_data.items() if v is not None}
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def validate(self) -> bool:
        """Validate that required API keys are present for configured providers."""
        if self.default_embedding_provider == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key required for OpenAI embedding provider")
        
        if self.default_chat_provider == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key required for OpenAI chat provider")
        
        if self.default_embedding_provider == "huggingface" and not self.huggingface_api_key:
            print("Warning: HuggingFace API key not set, using local models")
        
        if self.default_chat_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("Anthropic API key required for Anthropic chat provider")
        
        if self.default_embedding_provider == "openrouter" and not self.openrouter_api_key:
            raise ValueError("OpenRouter API key required for OpenRouter embedding provider")
        
        if self.default_chat_provider == "openrouter" and not self.openrouter_api_key:
            raise ValueError("OpenRouter API key required for OpenRouter chat provider")
        
        return True
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """Get configuration for embedding provider."""
        if self.default_embedding_provider == "openai":
            return {
                "provider": "openai",
                "model": self.openai_embedding_model,
                "api_key": self.openai_api_key
            }
        elif self.default_embedding_provider == "huggingface":
            return {
                "provider": "huggingface",
                "model": self.huggingface_embedding_model,
                "api_key": self.huggingface_api_key
            }
        elif self.default_embedding_provider == "openrouter":
            return {
                "provider": "openrouter",
                "model": self.openrouter_embedding_model,
                "api_key": self.openrouter_api_key
            }
        else:
            raise ValueError(f"Unsupported embedding provider: {self.default_embedding_provider}")
    
    def get_chat_config(self) -> Dict[str, Any]:
        """Get configuration for chat provider."""
        if self.default_chat_provider == "openai":
            return {
                "provider": "openai",
                "model": self.openai_chat_model,
                "api_key": self.openai_api_key,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
        elif self.default_chat_provider == "anthropic":
            return {
                "provider": "anthropic",
                "model": self.anthropic_chat_model,
                "api_key": self.anthropic_api_key,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
        elif self.default_chat_provider == "huggingface":
            return {
                "provider": "huggingface",
                "model": self.huggingface_chat_model,
                "api_key": self.huggingface_api_key,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
        elif self.default_chat_provider == "openrouter":
            return {
                "provider": "openrouter",
                "model": self.openrouter_chat_model,
                "api_key": self.openrouter_api_key,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
        else:
            raise ValueError(f"Unsupported chat provider: {self.default_chat_provider}")


# Global configuration instance
config = LLMConfig() 