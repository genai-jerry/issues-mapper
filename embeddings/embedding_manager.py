"""
Embedding Management Module

Handles embedding generation for code blocks using various providers.
"""

import hashlib
import pickle
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import os

try:
    from llm.llm_config import config, LLMConfig
    from vector_storage.vector_manager import VectorStorageManager
    from vector_storage.vector_models import VectorDocument
except ImportError:
    # Fallback for when running as module
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from llm.llm_config import config, LLMConfig
    from vector_storage.vector_manager import VectorStorageManager
    from vector_storage.vector_models import VectorDocument


class EmbeddingManager:
    """Manages embedding generation for code blocks."""
    
    def __init__(self, config_instance: Optional[LLMConfig] = None, 
                 vector_storage_type: str = "inmemory", vector_storage_config: Dict[str, Any] = None):
        self.config = config_instance or config
        self._embedding_cache = {}
        self._setup_cache()
        
        # Initialize vector storage
        self.vector_storage = VectorStorageManager(
            storage_type=vector_storage_type,
            config=vector_storage_config or {}
        )
        self.vector_storage.initialize()
    
    def _setup_cache(self):
        """Setup embedding cache directory."""
        if self.config.enable_cache:
            cache_dir = Path(self.config.cache_dir)
            cache_dir.mkdir(exist_ok=True)
            self.cache_dir = cache_dir
        else:
            self.cache_dir = None
    
    def _get_cache_key(self, text: str, model: str) -> str:
        """Generate cache key for text and model combination."""
        content = f"{text}:{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[float]]:
        """Retrieve embedding from cache."""
        if not self.config.enable_cache or not self.cache_dir:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not load from cache: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, embedding: List[float]):
        """Save embedding to cache."""
        if not self.config.enable_cache or not self.cache_dir:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except Exception as e:
            print(f"Warning: Could not save to cache: {e}")
    
    def _save_to_vector_db(self, collection: str, text: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """Save embedding to vector database."""
        if not self.vector_storage:
            print("Warning: Vector storage not configured")
            return
        
        try:
            # Create document
            document = VectorDocument(
                content=text,
                embedding=embedding,
                metadata=metadata or {}
            )
            
            # Store in vector database
            doc_ids = self.vector_storage.insert_documents(collection, [document])
            if doc_ids:
                print(f"Saved embedding to vector database (collection: {collection}, doc_id: {doc_ids[0]})")
            else:
                print("Warning: Failed to save embedding to vector database")
                
        except Exception as e:
            print(f"Warning: Could not save to vector database: {e}")
    
    def generate_embedding(self, text: str, model: Optional[str] = None,
                          save_to_vector_db: bool = False, collection: str = None,
                          metadata: Dict[str, Any] = None) -> List[float]:
        """Generate embedding for text using configured provider.
        
        Args:
            text: Text to generate embedding for
            model: Optional model override
            save_to_vector_db: Whether to save to vector database
            collection: Collection name for vector storage
            metadata: Metadata to store with the embedding
            
        Returns:
            List[float]: Embedding vector
        """
        if not text.strip():
            return [0.0] * 1536  # Default empty embedding
        
        # Get configuration
        embed_config = self.config.get_embedding_config()
        model = model or embed_config["model"]
        
        # Check cache first
        cache_key = self._get_cache_key(text, model)
        cached_embedding = self._get_from_cache(cache_key)
        if cached_embedding:
            # If saving to vector DB is requested, still save it
            if save_to_vector_db and collection:
                self._save_to_vector_db(collection, text, cached_embedding, metadata)
            return cached_embedding
        
        # Generate embedding
        try:
            embedding = self._generate_embedding_with_provider(text, embed_config, model)
            
            # Cache the result
            self._save_to_cache(cache_key, embedding)
            
            # Save to vector database if requested
            if save_to_vector_db and collection:
                self._save_to_vector_db(collection, text, embedding, metadata)
            
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Fallback to hash-based embedding
            fallback_embedding = self._generate_fallback_embedding(text)
            
            # Save fallback embedding to vector DB if requested
            if save_to_vector_db and collection:
                self._save_to_vector_db(collection, text, fallback_embedding, metadata)
            
            return fallback_embedding
    
    def _generate_embedding_with_provider(self, text: str, config: Dict[str, Any], model: str) -> List[float]:
        """Generate embedding using specific provider."""
        provider = config["provider"]
        print(f"Generating embedding with provider: {provider}")
        if provider == "openai":
            return self._generate_openai_embedding(text, model, config["api_key"])
        elif provider == "huggingface":
            return self._generate_huggingface_embedding(text, model, config["api_key"])
        elif provider == "openrouter":
            return self._generate_openrouter_embedding(text, model, config["api_key"])
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
    
    def _generate_openai_embedding(self, text: str, model: str, api_key: str) -> List[float]:
        """Generate embedding using OpenAI."""
        try:
            from langchain_openai import OpenAIEmbeddings
            
            embeddings = OpenAIEmbeddings(
                model=model,
                openai_api_key=api_key
            )
            return embeddings.embed_query(text)
            
        except ImportError:
            raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")
    
    def _generate_huggingface_embedding(self, text: str, model: str, api_key: Optional[str]) -> List[float]:
        """Generate embedding using HuggingFace."""
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            embeddings = HuggingFaceEmbeddings(
                model_name=model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            return embeddings.embed_query(text)
            
        except ImportError:
            raise ImportError("langchain-community not installed. Run: pip install langchain-community")
    
    def _generate_openrouter_embedding(self, text: str, model: str, api_key: str) -> List[float]:
        """Generate embedding using OpenRouter."""
        try:
            from langchain_openai import OpenAIEmbeddings
            
            embeddings = OpenAIEmbeddings(
                model=model,
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1"
            )
            return embeddings.embed_query(text)
            
        except ImportError:
            raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")
    
    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """Generate a simple hash-based embedding as fallback."""
        # Create a deterministic hash-based embedding
        hash_value = hash(text)
        # Convert to a list of floats
        embedding = []
        for i in range(1536):  # Standard embedding size
            # Use hash with different seeds to generate embedding
            seed = hash_value + i * 31
            embedding.append(float(seed % 1000) / 1000.0)
        return embedding
    
    def batch_generate_embeddings(self, texts: List[str], model: Optional[str] = None,
                                 save_to_vector_db: bool = False, collection: str = None,
                                 metadata_list: List[Dict[str, Any]] = None) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to generate embeddings for
            model: Optional model override
            save_to_vector_db: Whether to save to vector database
            collection: Collection name for vector storage
            metadata_list: List of metadata dictionaries for each text
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else None
            embedding = self.generate_embedding(
                text, model, 
                save_to_vector_db=save_to_vector_db, 
                collection=collection, 
                metadata=metadata
            )
            embeddings.append(embedding)
        
        return embeddings
    
    def clear_cache(self):
        """Clear the embedding cache."""
        if self.cache_dir and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            print(f"Cleared {len(list(self.cache_dir.glob('*.pkl')))} cached embeddings")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache_dir or not self.cache_dir.exists():
            return {"enabled": False, "cache_dir": None, "file_count": 0}
        
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "enabled": self.config.enable_cache,
            "cache_dir": str(self.cache_dir),
            "file_count": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    # Vector Storage Methods
    
    def store_embedding(self, collection: str, content: str, metadata: Dict[str, Any] = None, 
                       model: Optional[str] = None) -> str:
        """Store content with its embedding in vector storage.
        
        Args:
            collection: Collection name
            content: Text content to store
            metadata: Additional metadata
            model: Optional model override
            
        Returns:
            str: Document ID
        """
        # Generate embedding
        embedding = self.generate_embedding(content, model)
        
        # Create document
        document = VectorDocument(
            content=content,
            embedding=embedding,
            metadata=metadata or {}
        )
        
        # Store in vector database
        doc_ids = self.vector_storage.insert_documents(collection, [document])
        return doc_ids[0] if doc_ids else None
    
    def store_batch(self, collection: str, documents: List[Dict[str, Any]], 
                   model: Optional[str] = None) -> List[str]:
        """Store multiple documents with embeddings.
        
        Args:
            collection: Collection name
            documents: List of documents with 'content' and optional 'metadata' keys
            model: Optional model override
            
        Returns:
            List[str]: Document IDs
        """
        vector_docs = []
        
        for doc_data in documents:
            content = doc_data['content']
            metadata = doc_data.get('metadata', {})
            
            # Generate embedding
            embedding = self.generate_embedding(content, model)
            
            # Create vector document
            vector_doc = VectorDocument(
                content=content,
                embedding=embedding,
                metadata=metadata
            )
            vector_docs.append(vector_doc)
        
        # Store in vector database
        return self.vector_storage.insert_documents(collection, vector_docs)
    
    def search_similar(self, collection: str, query: str, limit: int = 10, 
                      filter_metadata: Dict[str, Any] = None, model: Optional[str] = None) -> List[Tuple[str, float]]:
        """Search for similar content.
        
        Args:
            collection: Collection name
            query: Search query
            limit: Maximum number of results
            filter_metadata: Metadata filter
            model: Optional model override
            
        Returns:
            List[Tuple[str, float]]: List of (content, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query, model)
        
        # Search in vector database
        results = self.vector_storage.search_similar(
            collection, query_embedding, limit, filter_metadata
        )
        
        # Return content and similarity scores
        return [(doc.content, score) for doc, score in results]
    
    def get_document(self, collection: str, document_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        return self.vector_storage.get_document(collection, document_id)
    
    def update_document(self, collection: str, document_id: str, content: str = None, 
                       metadata: Dict[str, Any] = None, model: Optional[str] = None) -> bool:
        """Update a document.
        
        Args:
            collection: Collection name
            document_id: Document ID
            content: New content (optional)
            metadata: New metadata (optional)
            model: Optional model override for new embedding
            
        Returns:
            bool: Success status
        """
        if content is not None:
            # Generate new embedding for updated content
            embedding = self.generate_embedding(content, model)
            return self.vector_storage.update_document(
                collection, document_id, content=content, 
                embedding=embedding, metadata=metadata
            )
        else:
            return self.vector_storage.update_document(
                collection, document_id, metadata=metadata
            )
    
    def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        return self.vector_storage.delete_document(collection, document_id)
    
    def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get collection statistics."""
        count = self.vector_storage.get_collection_count(collection)
        return {
            "collection": collection,
            "document_count": count,
            "storage_type": self.vector_storage.storage_type
        }
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        return self.vector_storage.list_collections()
    
    def create_collection(self, name: str, dimension: int = 1536) -> bool:
        """Create a new collection."""
        return self.vector_storage.create_collection(name, dimension)
    
    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        return self.vector_storage.delete_collection(name)
    
    def clear_collection(self, name: str) -> bool:
        """Clear all documents in a collection."""
        return self.vector_storage.clear_collection(name)
    
    def switch_vector_storage(self, storage_type: str, config: Dict[str, Any] = None) -> bool:
        """Switch to a different vector storage type."""
        return self.vector_storage.switch_storage(storage_type, config) 