"""
Vector Storage Configuration

This module handles configuration for vector storage backends.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class VectorStorageConfig:
    """Configuration for vector storage backends."""
    
    storage_type: str = "chroma"
    persist_directory: str = "chroma_db"
    api_key: Optional[str] = None
    environment: Optional[str] = None
    collection_name: str = "default"
    embedding_dimension: int = 1536
    distance_metric: str = "cosine"
    
    def __post_init__(self):
        """Load configuration from file if available."""
        if os.path.exists("vector_storage_config.json"):
            self.load_from_file("vector_storage_config.json")
    
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
            'storage_type': self.storage_type,
            'persist_directory': self.persist_directory,
            'api_key': self.api_key,
            'environment': self.environment,
            'collection_name': self.collection_name,
            'embedding_dimension': self.embedding_dimension,
            'distance_metric': self.distance_metric
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage-specific configuration."""
        if self.storage_type == "chroma":
            return {
                "persist_directory": self.persist_directory,
                "collection_name": self.collection_name
            }
        elif self.storage_type == "pinecone":
            return {
                "api_key": self.api_key,
                "environment": self.environment,
                "collection_name": self.collection_name
            }
        else:
            return {} 