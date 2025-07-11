"""
Vector Storage Module

Provides abstract interfaces and implementations for vector database storage.
Supports multiple vector databases with a unified CRUD interface.
"""

import json
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np

from .vector_models import VectorDocument


class VectorStorage(ABC):
    """Abstract base class for vector storage implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize vector storage with configuration."""
        self.config = config
        self.initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the vector storage."""
        pass
    
    @abstractmethod
    def create_collection(self, name: str, dimension: int = 1536) -> bool:
        """Create a new collection."""
        pass
    
    @abstractmethod
    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        pass
    
    @abstractmethod
    def list_collections(self) -> List[str]:
        """List all collections."""
        pass
    
    @abstractmethod
    def insert(self, collection: str, documents: List[VectorDocument]) -> List[str]:
        """Insert documents into collection."""
        pass
    
    @abstractmethod
    def get(self, collection: str, document_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    def update(self, collection: str, document_id: str, content: str = None, 
               embedding: List[float] = None, metadata: Dict[str, Any] = None) -> bool:
        """Update a document."""
        pass
    
    @abstractmethod
    def delete(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        pass
    
    @abstractmethod
    def search(self, collection: str, query_embedding: List[float], 
               limit: int = 10, filter_metadata: Dict[str, Any] = None) -> List[Tuple[VectorDocument, float]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    def count(self, collection: str) -> int:
        """Get document count in collection."""
        pass
    
    @abstractmethod
    def clear(self, collection: str) -> bool:
        """Clear all documents in collection."""
        pass


class InMemoryVectorStorage(VectorStorage):
    """Simple in-memory vector storage for testing and development."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.collections: Dict[str, Dict[str, VectorDocument]] = {}
        self.embeddings: Dict[str, Dict[str, List[float]]] = {}
    
    def initialize(self) -> bool:
        """Initialize in-memory storage."""
        self.initialized = True
        return True
    
    def create_collection(self, name: str, dimension: int = 1536) -> bool:
        """Create a new collection."""
        if not self.initialized:
            return False
        
        if name not in self.collections:
            self.collections[name] = {}
            self.embeddings[name] = {}
        return True
    
    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        if name in self.collections:
            del self.collections[name]
            del self.embeddings[name]
            return True
        return False
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        return list(self.collections.keys())
    
    def insert(self, collection: str, documents: List[VectorDocument]) -> List[str]:
        """Insert documents into collection."""
        if collection not in self.collections:
            self.create_collection(collection)
        
        inserted_ids = []
        for doc in documents:
            self.collections[collection][doc.id] = doc
            self.embeddings[collection][doc.id] = doc.embedding
            inserted_ids.append(doc.id)
        
        return inserted_ids
    
    def get(self, collection: str, document_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        return self.collections.get(collection, {}).get(document_id)
    
    def update(self, collection: str, document_id: str, content: str = None, 
               embedding: List[float] = None, metadata: Dict[str, Any] = None) -> bool:
        """Update a document."""
        if collection not in self.collections or document_id not in self.collections[collection]:
            return False
        
        doc = self.collections[collection][document_id]
        
        if content is not None:
            doc.content = content
        if embedding is not None:
            doc.embedding = embedding
            self.embeddings[collection][document_id] = embedding
        if metadata is not None:
            doc.metadata.update(metadata)
        
        doc.updated_at = datetime.now()
        return True
    
    def delete(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        if collection in self.collections and document_id in self.collections[collection]:
            del self.collections[collection][document_id]
            if document_id in self.embeddings[collection]:
                del self.embeddings[collection][document_id]
            return True
        return False
    
    def search(self, collection: str, query_embedding: List[float], 
               limit: int = 10, filter_metadata: Dict[str, Any] = None) -> List[Tuple[VectorDocument, float]]:
        """Search for similar documents using cosine similarity."""
        if collection not in self.collections:
            return []
        
        results = []
        query_norm = np.linalg.norm(query_embedding)
        
        for doc_id, doc in self.collections[collection].items():
            # Apply metadata filter if provided
            if filter_metadata:
                if not all(doc.metadata.get(k) == v for k, v in filter_metadata.items()):
                    continue
            
            # Calculate cosine similarity
            doc_embedding = self.embeddings[collection][doc_id]
            dot_product = np.dot(query_embedding, doc_embedding)
            doc_norm = np.linalg.norm(doc_embedding)
            
            if doc_norm > 0:
                similarity = dot_product / (query_norm * doc_norm)
                results.append((doc, similarity))
        
        # Sort by similarity (descending) and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def count(self, collection: str) -> int:
        """Get document count in collection."""
        return len(self.collections.get(collection, {}))
    
    def clear(self, collection: str) -> bool:
        """Clear all documents in collection."""
        if collection in self.collections:
            self.collections[collection].clear()
            self.embeddings[collection].clear()
            return True
        return False


class ChromaVectorStorage(VectorStorage):
    """Chroma vector database storage implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self.collections = {}
    
    def initialize(self) -> bool:
        """Initialize Chroma client."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Get configuration
            persist_directory = self.config.get("persist_directory", "./chroma_db")
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 8000)
            
            if self.config.get("use_http_client", False):
                # Use HTTP client for remote Chroma
                self.client = chromadb.HttpClient(
                    host=host,
                    port=port
                )
            else:
                # Use persistent client for local Chroma
                self.client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False
                    )
                )
            
            self.initialized = True
            return True
            
        except ImportError:
            print("ChromaDB not installed. Run: pip install chromadb")
            return False
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            return False
    
    def create_collection(self, name: str, dimension: int = 1536) -> bool:
        """Create a new collection."""
        if not self.initialized:
            return False
        
        try:
            collection = self.client.create_collection(
                name=name,
                metadata={"dimension": dimension}
            )
            self.collections[name] = collection
            return True
        except Exception as e:
            print(f"Error creating collection {name}: {e}")
            return False
    
    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        if not self.initialized:
            return False
        
        try:
            self.client.delete_collection(name=name)
            if name in self.collections:
                del self.collections[name]
            return True
        except Exception as e:
            print(f"Error deleting collection {name}: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        if not self.initialized:
            return []
        
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []
    
    def _get_collection(self, name: str):
        """Get or create collection."""
        if name not in self.collections:
            try:
                self.collections[name] = self.client.get_collection(name=name)
            except:
                self.create_collection(name)
        return self.collections.get(name)
    
    def insert(self, collection: str, documents: List[VectorDocument]) -> List[str]:
        """Insert documents into collection."""
        chroma_collection = self._get_collection(collection)
        if not chroma_collection:
            return []
        
        try:
            ids = [doc.id for doc in documents]
            embeddings = [doc.embedding for doc in documents]
            contents = [doc.content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            chroma_collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            
            return ids
        except Exception as e:
            print(f"Error inserting documents: {e}")
            return []
    
    def get(self, collection: str, document_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        chroma_collection = self._get_collection(collection)
        if not chroma_collection:
            return None
        
        try:
            result = chroma_collection.get(ids=[document_id])
            if result['ids']:
                return VectorDocument(
                    id=result['ids'][0],
                    content=result['documents'][0],
                    embedding=result['embeddings'][0],
                    metadata=result['metadatas'][0] if result['metadatas'] else {},
                    created_at=datetime.now(),  # Chroma doesn't store timestamps
                    updated_at=datetime.now()
                )
        except Exception as e:
            print(f"Error getting document: {e}")
        
        return None
    
    def update(self, collection: str, document_id: str, content: str = None, 
               embedding: List[float] = None, metadata: Dict[str, Any] = None) -> bool:
        """Update a document."""
        chroma_collection = self._get_collection(collection)
        if not chroma_collection:
            return False
        
        try:
            update_data = {}
            if content is not None:
                update_data['documents'] = [content]
            if embedding is not None:
                update_data['embeddings'] = [embedding]
            if metadata is not None:
                update_data['metadatas'] = [metadata]
            
            if update_data:
                chroma_collection.update(
                    ids=[document_id],
                    **update_data
                )
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    def delete(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        chroma_collection = self._get_collection(collection)
        if not chroma_collection:
            return False
        
        try:
            chroma_collection.delete(ids=[document_id])
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def search(self, collection: str, query_embedding: List[float], 
               limit: int = 10, filter_metadata: Dict[str, Any] = None) -> List[Tuple[VectorDocument, float]]:
        """Search for similar documents."""
        chroma_collection = self._get_collection(collection)
        if not chroma_collection:
            return []
        
        try:
            where = filter_metadata if filter_metadata else None
            
            result = chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where
            )
            
            results = []
            if result['ids'] and result['ids'][0]:
                for i, doc_id in enumerate(result['ids'][0]):
                    doc = VectorDocument(
                        id=doc_id,
                        content=result['documents'][0][i],
                        embedding=result['embeddings'][0][i],
                        metadata=result['metadatas'][0][i] if result['metadatas'] else {},
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    distance = result['distances'][0][i]
                    similarity = 1 - distance  # Convert distance to similarity
                    results.append((doc, similarity))
            
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def count(self, collection: str) -> int:
        """Get document count in collection."""
        chroma_collection = self._get_collection(collection)
        if not chroma_collection:
            return 0
        
        try:
            return chroma_collection.count()
        except Exception as e:
            print(f"Error counting documents: {e}")
            return 0
    
    def clear(self, collection: str) -> bool:
        """Clear all documents in collection."""
        chroma_collection = self._get_collection(collection)
        if not chroma_collection:
            return False
        
        try:
            # Get all IDs and delete them
            result = chroma_collection.get()
            if result['ids']:
                chroma_collection.delete(ids=result['ids'])
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False


class PineconeVectorStorage(VectorStorage):
    """Pinecone vector database storage implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.index = None
    
    def initialize(self) -> bool:
        """Initialize Pinecone client."""
        try:
            import pinecone
            
            api_key = self.config.get("api_key")
            environment = self.config.get("environment")
            
            if not api_key or not environment:
                print("Pinecone API key and environment required")
                return False
            
            pinecone.init(api_key=api_key, environment=environment)
            self.initialized = True
            return True
            
        except ImportError:
            print("Pinecone not installed. Run: pip install pinecone-client")
            return False
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return False
    
    def create_collection(self, name: str, dimension: int = 1536) -> bool:
        """Create a new index (Pinecone uses indexes instead of collections)."""
        if not self.initialized:
            return False
        
        try:
            import pinecone
            
            # Check if index already exists
            if name in pinecone.list_indexes():
                return True
            
            # Create new index
            pinecone.create_index(
                name=name,
                dimension=dimension,
                metric="cosine"
            )
            return True
        except Exception as e:
            print(f"Error creating Pinecone index {name}: {e}")
            return False
    
    def delete_collection(self, name: str) -> bool:
        """Delete an index."""
        if not self.initialized:
            return False
        
        try:
            import pinecone
            pinecone.delete_index(name)
            return True
        except Exception as e:
            print(f"Error deleting Pinecone index {name}: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """List all indexes."""
        if not self.initialized:
            return []
        
        try:
            import pinecone
            return pinecone.list_indexes()
        except Exception as e:
            print(f"Error listing Pinecone indexes: {e}")
            return []
    
    def _get_index(self, name: str):
        """Get Pinecone index."""
        if not self.index or self.index.name != name:
            try:
                import pinecone
                self.index = pinecone.Index(name)
            except Exception as e:
                print(f"Error getting Pinecone index {name}: {e}")
                return None
        return self.index
    
    def insert(self, collection: str, documents: List[VectorDocument]) -> List[str]:
        """Insert documents into index."""
        index = self._get_index(collection)
        if not index:
            return []
        
        try:
            vectors = []
            for doc in documents:
                vectors.append({
                    'id': doc.id,
                    'values': doc.embedding,
                    'metadata': {
                        'content': doc.content,
                        **doc.metadata
                    }
                })
            
            index.upsert(vectors=vectors)
            return [doc.id for doc in documents]
        except Exception as e:
            print(f"Error inserting documents to Pinecone: {e}")
            return []
    
    def get(self, collection: str, document_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        index = self._get_index(collection)
        if not index:
            return None
        
        try:
            result = index.fetch(ids=[document_id])
            if document_id in result['vectors']:
                vector_data = result['vectors'][document_id]
                return VectorDocument(
                    id=document_id,
                    content=vector_data['metadata']['content'],
                    embedding=vector_data['values'],
                    metadata={k: v for k, v in vector_data['metadata'].items() if k != 'content'},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
        except Exception as e:
            print(f"Error getting document from Pinecone: {e}")
        
        return None
    
    def update(self, collection: str, document_id: str, content: str = None, 
               embedding: List[float] = None, metadata: Dict[str, Any] = None) -> bool:
        """Update a document."""
        index = self._get_index(collection)
        if not index:
            return False
        
        try:
            update_data = {'id': document_id}
            if embedding is not None:
                update_data['values'] = embedding
            if content is not None or metadata is not None:
                current_metadata = {}
                if content is not None:
                    current_metadata['content'] = content
                if metadata is not None:
                    current_metadata.update(metadata)
                update_data['metadata'] = current_metadata
            
            index.upsert(vectors=[update_data])
            return True
        except Exception as e:
            print(f"Error updating document in Pinecone: {e}")
            return False
    
    def delete(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        index = self._get_index(collection)
        if not index:
            return False
        
        try:
            index.delete(ids=[document_id])
            return True
        except Exception as e:
            print(f"Error deleting document from Pinecone: {e}")
            return False
    
    def search(self, collection: str, query_embedding: List[float], 
               limit: int = 10, filter_metadata: Dict[str, Any] = None) -> List[Tuple[VectorDocument, float]]:
        """Search for similar documents."""
        index = self._get_index(collection)
        if not index:
            return []
        
        try:
            query_response = index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                filter=filter_metadata
            )
            
            results = []
            for match in query_response['matches']:
                doc = VectorDocument(
                    id=match['id'],
                    content=match['metadata']['content'],
                    embedding=match['values'],
                    metadata={k: v for k, v in match['metadata'].items() if k != 'content'},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                results.append((doc, match['score']))
            
            return results
        except Exception as e:
            print(f"Error searching documents in Pinecone: {e}")
            return []
    
    def count(self, collection: str) -> int:
        """Get document count in index."""
        index = self._get_index(collection)
        if not index:
            return 0
        
        try:
            stats = index.describe_index_stats()
            return stats['total_vector_count']
        except Exception as e:
            print(f"Error counting documents in Pinecone: {e}")
            return 0
    
    def clear(self, collection: str) -> bool:
        """Clear all documents in index."""
        index = self._get_index(collection)
        if not index:
            return False
        
        try:
            # Delete all vectors by deleting the index and recreating it
            import pinecone
            pinecone.delete_index(collection)
            self.create_collection(collection)
            return True
        except Exception as e:
            print(f"Error clearing Pinecone index: {e}")
            return False


class VectorStorageManager:
    """Manager class for vector storage operations."""
    
    def __init__(self, storage_type: str = "inmemory", config: Dict[str, Any] = None):
        """Initialize vector storage manager."""
        self.storage_type = storage_type
        self.config = config or {}
        self.storage = self._create_storage()
    
    def _create_storage(self) -> VectorStorage:
        """Create storage instance based on type."""
        if self.storage_type == "inmemory":
            return InMemoryVectorStorage(self.config)
        elif self.storage_type == "chroma":
            return ChromaVectorStorage(self.config)
        elif self.storage_type == "pinecone":
            return PineconeVectorStorage(self.config)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def initialize(self) -> bool:
        """Initialize the storage."""
        return self.storage.initialize()
    
    def create_collection(self, name: str, dimension: int = 1536) -> bool:
        """Create a new collection."""
        return self.storage.create_collection(name, dimension)
    
    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        return self.storage.delete_collection(name)
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        return self.storage.list_collections()
    
    def insert_documents(self, collection: str, documents: List[VectorDocument]) -> List[str]:
        """Insert documents into collection."""
        return self.storage.insert(collection, documents)
    
    def get_document(self, collection: str, document_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        return self.storage.get(collection, document_id)
    
    def update_document(self, collection: str, document_id: str, **kwargs) -> bool:
        """Update a document."""
        return self.storage.update(collection, document_id, **kwargs)
    
    def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        return self.storage.delete(collection, document_id)
    
    def search_similar(self, collection: str, query_embedding: List[float], 
                      limit: int = 10, filter_metadata: Dict[str, Any] = None) -> List[Tuple[VectorDocument, float]]:
        """Search for similar documents."""
        return self.storage.search(collection, query_embedding, limit, filter_metadata)
    
    def get_collection_count(self, collection: str) -> int:
        """Get document count in collection."""
        return self.storage.count(collection)
    
    def clear_collection(self, collection: str) -> bool:
        """Clear all documents in collection."""
        return self.storage.clear(collection)
    
    def switch_storage(self, storage_type: str, config: Dict[str, Any] = None) -> bool:
        """Switch to a different storage type."""
        self.storage_type = storage_type
        self.config = config or {}
        self.storage = self._create_storage()
        return self.storage.initialize() 