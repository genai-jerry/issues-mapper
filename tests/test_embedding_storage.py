#!/usr/bin/env python3
"""
Simple test script to verify embedding storage functionality.
"""

import os
import sys

# Add the mvp directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mvp'))

from llm.config import LLMConfig
from llm.embeddings import EmbeddingManager

def test_embedding_storage():
    """Test basic embedding storage functionality."""
    print("Testing embedding storage functionality...")
    
    # Setup configuration
    config = LLMConfig()
    config.embedding_provider = "openai"
    config.embedding_model = "text-embedding-ada-002"
    config.embedding_api_key = os.getenv("OPENAI_API_KEY")
    config.enable_cache = True
    
    # Initialize embedding manager with ChromaDB
    embedding_manager = EmbeddingManager(
        config_instance=config,
        vector_storage_type="chroma",
        vector_storage_config={
            "persist_directory": "test_chroma_db"
        }
    )
    
    # Create test collection
    collection_name = "test_collection"
    embedding_manager.create_collection(collection_name, dimension=1536)
    
    # Test text
    test_text = "This is a test document for embedding storage."
    
    # Generate embedding and save to vector database
    print(f"Generating embedding for: '{test_text}'")
    embedding = embedding_manager.generate_embedding(
        text=test_text,
        save_to_vector_db=True,
        collection=collection_name,
        metadata={"test": True, "source": "test_script"}
    )
    
    print(f"Generated embedding (length: {len(embedding)})")
    
    # Search for similar content
    print("\nSearching for similar content...")
    results = embedding_manager.search_similar(
        collection=collection_name,
        query="test document",
        limit=5
    )
    
    print(f"Found {len(results)} similar documents:")
    for i, (doc_id, similarity) in enumerate(results, 1):
        doc = embedding_manager.get_document(collection_name, doc_id)
        if doc:
            print(f"  {i}. Similarity: {similarity:.4f}")
            print(f"     Content: {doc.content}")
            print(f"     Metadata: {doc.metadata}")
    
    # Get collection stats
    stats = embedding_manager.get_collection_stats(collection_name)
    print(f"\nCollection statistics: {stats}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_embedding_storage() 