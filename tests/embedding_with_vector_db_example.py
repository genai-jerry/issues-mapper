#!/usr/bin/env python3
"""
Example script demonstrating embedding generation with vector database storage.

This script shows how to:
1. Generate embeddings and save them to ChromaDB
2. Use different vector storage backends
3. Search for similar content
4. Manage collections
"""

import os
import sys
from typing import List, Dict, Any
from datetime import datetime

# Add the mvp directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mvp'))

from llm.config import LLMConfig
from llm.embeddings import EmbeddingManager
from llm.vector_storage import VectorDocument

def setup_config():
    """Setup LLM configuration with embedding settings."""
    config = LLMConfig()
    
    # Set embedding configuration
    config.embedding_provider = "openai"  # or "openrouter", "huggingface"
    config.embedding_model = "text-embedding-ada-002"
    config.embedding_api_key = os.getenv("OPENAI_API_KEY")
    
    # Enable caching
    config.enable_cache = True
    config.cache_dir = "embedding_cache"
    
    return config

def example_basic_embedding_with_storage():
    """Example: Generate embedding and save to vector database."""
    print("=" * 60)
    print("BASIC EMBEDDING WITH VECTOR STORAGE")
    print("=" * 60)
    
    # Setup configuration
    config = setup_config()
    
    # Initialize embedding manager with ChromaDB
    embedding_manager = EmbeddingManager(
        config_instance=config,
        vector_storage_type="chroma",
        vector_storage_config={
            "persist_directory": "chroma_db",
            "collection_name": "documents"
        }
    )
    
    # Create collection
    embedding_manager.create_collection("documents", dimension=1536)
    
    # Sample texts
    texts = [
        "Python is a high-level programming language known for its simplicity and readability.",
        "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
        "Vector databases store and retrieve high-dimensional vector data efficiently for similarity search.",
        "Natural language processing (NLP) is a field of AI that focuses on the interaction between computers and human language.",
        "ChromaDB is an open-source embedding database designed for AI applications."
    ]
    
    # Generate embeddings and save to vector database
    print("\nGenerating embeddings and saving to vector database...")
    for i, text in enumerate(texts):
        metadata = {
            "source": "example",
            "category": "programming" if "programming" in text.lower() else "ai",
            "timestamp": datetime.now().isoformat(),
            "index": i
        }
        
        embedding = embedding_manager.generate_embedding(
            text=text,
            save_to_vector_db=True,
            collection="documents",
            metadata=metadata
        )
        
        print(f"Generated embedding for text {i+1} (length: {len(embedding)})")
    
    print(f"\nSaved {len(texts)} embeddings to vector database")

def example_batch_embedding_with_storage():
    """Example: Batch generate embeddings and save to vector database."""
    print("\n" + "=" * 60)
    print("BATCH EMBEDDING WITH VECTOR STORAGE")
    print("=" * 60)
    
    # Setup configuration
    config = setup_config()
    
    # Initialize embedding manager
    embedding_manager = EmbeddingManager(
        config_instance=config,
        vector_storage_type="chroma"
    )
    
    # Sample documents with metadata
    documents = [
        {
            "content": "The quick brown fox jumps over the lazy dog.",
            "metadata": {"category": "animals", "difficulty": "easy"}
        },
        {
            "content": "Quantum computing uses quantum mechanical phenomena to process information.",
            "metadata": {"category": "technology", "difficulty": "hard"}
        },
        {
            "content": "Data science combines statistics, programming, and domain expertise.",
            "metadata": {"category": "science", "difficulty": "medium"}
        }
    ]
    
    # Extract texts and metadata
    texts = [doc["content"] for doc in documents]
    metadata_list = [doc["metadata"] for doc in documents]
    
    # Batch generate embeddings and save to vector database
    print("\nBatch generating embeddings...")
    embeddings = embedding_manager.batch_generate_embeddings(
        texts=texts,
        save_to_vector_db=True,
        collection="documents",
        metadata_list=metadata_list
    )
    
    print(f"Generated {len(embeddings)} embeddings in batch")

def example_search_similar():
    """Example: Search for similar content in vector database."""
    print("\n" + "=" * 60)
    print("SEARCHING SIMILAR CONTENT")
    print("=" * 60)
    
    # Setup configuration
    config = setup_config()
    
    # Initialize embedding manager
    embedding_manager = EmbeddingManager(
        config_instance=config,
        vector_storage_type="chroma"
    )
    
    # Search queries
    search_queries = [
        "What is artificial intelligence?",
        "How does programming work?",
        "Tell me about databases",
        "Machine learning algorithms"
    ]
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        
        # Search for similar content
        results = embedding_manager.search_similar(
            collection="documents",
            query=query,
            limit=3
        )
        
        print(f"Found {len(results)} similar documents:")
        for i, (doc_id, similarity) in enumerate(results, 1):
            # Get the document
            doc = embedding_manager.get_document("documents", doc_id)
            if doc:
                print(f"  {i}. Similarity: {similarity:.4f}")
                print(f"     Content: {doc.content[:100]}...")
                print(f"     Metadata: {doc.metadata}")

def example_collection_management():
    """Example: Managing collections in vector database."""
    print("\n" + "=" * 60)
    print("COLLECTION MANAGEMENT")
    print("=" * 60)
    
    # Setup configuration
    config = setup_config()
    
    # Initialize embedding manager
    embedding_manager = EmbeddingManager(
        config_instance=config,
        vector_storage_type="chroma"
    )
    
    # List existing collections
    collections = embedding_manager.list_collections()
    print(f"Existing collections: {collections}")
    
    # Create a new collection
    new_collection = "test_collection"
    if embedding_manager.create_collection(new_collection, dimension=1536):
        print(f"Created collection: {new_collection}")
    
    # Add some documents to the new collection
    test_texts = [
        "This is a test document for collection management.",
        "Another test document to demonstrate functionality."
    ]
    
    for text in test_texts:
        embedding_manager.generate_embedding(
            text=text,
            save_to_vector_db=True,
            collection=new_collection,
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
    
    # Get collection statistics
    stats = embedding_manager.get_collection_stats(new_collection)
    print(f"\nCollection '{new_collection}' statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # List collections again
    collections = embedding_manager.list_collections()
    print(f"\nUpdated collections: {collections}")

def example_different_storage_backends():
    """Example: Using different vector storage backends."""
    print("\n" + "=" * 60)
    print("DIFFERENT STORAGE BACKENDS")
    print("=" * 60)
    
    # Setup configuration
    config = setup_config()
    
    # Test different storage backends
    storage_configs = [
        ("inmemory", {}, "In-Memory Storage"),
        ("chroma", {"persist_directory": "chroma_db"}, "ChromaDB Storage"),
        # ("pinecone", {"api_key": "your-pinecone-key", "environment": "your-environment"}, "Pinecone Storage")
    ]
    
    for storage_type, storage_config, description in storage_configs:
        print(f"\n--- {description} ---")
        
        try:
            # Initialize embedding manager with different storage
            embedding_manager = EmbeddingManager(
                config_instance=config,
                vector_storage_type=storage_type,
                vector_storage_config=storage_config
            )
            
            # Create collection
            collection_name = f"test_{storage_type}"
            embedding_manager.create_collection(collection_name, dimension=1536)
            
            # Generate and store embedding
            text = f"Test document for {storage_type} storage"
            embedding = embedding_manager.generate_embedding(
                text=text,
                save_to_vector_db=True,
                collection=collection_name,
                metadata={"storage_type": storage_type}
            )
            
            print(f"Successfully stored embedding using {storage_type}")
            
            # Get collection stats
            stats = embedding_manager.get_collection_stats(collection_name)
            print(f"Collection stats: {stats}")
            
        except Exception as e:
            print(f"Error with {storage_type}: {e}")

def main():
    """Run all examples."""
    print("EMBEDDING WITH VECTOR DATABASE EXAMPLES")
    print("=" * 60)
    
    try:
        # Run examples
        example_basic_embedding_with_storage()
        example_batch_embedding_with_storage()
        example_search_similar()
        example_collection_management()
        example_different_storage_backends()
        
        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 