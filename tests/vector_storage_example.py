#!/usr/bin/env python3
"""
Vector Storage Example for Issues Manager MVP

This script demonstrates how to use the vector storage functionality
with different storage backends (InMemory, ChromaDB, Pinecone).
"""

import json
from typing import Dict, Any
from llm import LLMConfig, EmbeddingManager, VectorStorageManager, VectorDocument


def demonstrate_inmemory_storage():
    """Demonstrate in-memory vector storage."""
    print("=== In-Memory Vector Storage Demo ===")
    
    # Create embedding manager with in-memory storage
    embedding_manager = EmbeddingManager(
        vector_storage_type="inmemory"
    )
    
    # Create a collection
    collection_name = "code_snippets"
    embedding_manager.create_collection(collection_name)
    print(f"✅ Created collection: {collection_name}")
    
    # Store some code snippets
    code_snippets = [
        {
            "content": """
def fibonacci(n):
    '''Calculate the nth Fibonacci number.'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""",
            "metadata": {
                "language": "python",
                "category": "algorithms",
                "difficulty": "easy"
            }
        },
        {
            "content": """
def quicksort(arr):
    '''Sort array using quicksort algorithm.'''
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
""",
            "metadata": {
                "language": "python",
                "category": "algorithms",
                "difficulty": "medium"
            }
        },
        {
            "content": """
class DatabaseConnection:
    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database
        self.connection = None
    
    def connect(self):
        # Database connection logic
        pass
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
""",
            "metadata": {
                "language": "python",
                "category": "database",
                "difficulty": "medium"
            }
        }
    ]
    
    # Store documents
    doc_ids = embedding_manager.store_batch(collection_name, code_snippets)
    print(f"✅ Stored {len(doc_ids)} documents")
    
    # Search for similar code
    print("\n🔍 Searching for 'sorting algorithms':")
    results = embedding_manager.search_similar(collection_name, "sorting algorithms", limit=2)
    for content, score in results:
        print(f"Score: {score:.3f}")
        print(f"Content: {content[:100]}...")
        print()
    
    # Get collection stats
    stats = embedding_manager.get_collection_stats(collection_name)
    print(f"📊 Collection stats: {stats}")
    
    # Update a document
    if doc_ids:
        success = embedding_manager.update_document(
            collection_name, doc_ids[0], 
            metadata={"difficulty": "hard", "updated": True}
        )
        print(f"✅ Updated document: {success}")
    
    # Get a specific document
    if doc_ids:
        doc = embedding_manager.get_document(collection_name, doc_ids[0])
        print(f"📄 Retrieved document: {doc.id}")
        print(f"Metadata: {doc.metadata}")


def demonstrate_chroma_storage():
    """Demonstrate ChromaDB vector storage."""
    print("\n=== ChromaDB Vector Storage Demo ===")
    
    # ChromaDB configuration
    chroma_config = {
        "persist_directory": "./chroma_db",
        "use_http_client": False  # Use local persistent storage
    }
    
    try:
        # Create embedding manager with ChromaDB storage
        embedding_manager = EmbeddingManager(
            vector_storage_type="chroma",
            vector_storage_config=chroma_config
        )
        
        # Create a collection
        collection_name = "documentation"
        embedding_manager.create_collection(collection_name)
        print(f"✅ Created ChromaDB collection: {collection_name}")
        
        # Store documentation snippets
        docs = [
            {
                "content": "FastAPI is a modern web framework for building APIs with Python based on standard Python type hints.",
                "metadata": {"framework": "fastapi", "type": "introduction"}
            },
            {
                "content": "SQLAlchemy is a SQL toolkit and Object-Relational Mapping library for Python.",
                "metadata": {"framework": "sqlalchemy", "type": "introduction"}
            },
            {
                "content": "Pydantic is a data validation library using Python type annotations.",
                "metadata": {"framework": "pydantic", "type": "introduction"}
            }
        ]
        
        doc_ids = embedding_manager.store_batch(collection_name, docs)
        print(f"✅ Stored {len(doc_ids)} documents in ChromaDB")
        
        # Search
        print("\n🔍 Searching for 'data validation':")
        results = embedding_manager.search_similar(collection_name, "data validation", limit=2)
        for content, score in results:
            print(f"Score: {score:.3f}")
            print(f"Content: {content}")
            print()
        
        # List collections
        collections = embedding_manager.list_collections()
        print(f"📁 Available collections: {collections}")
        
    except Exception as e:
        print(f"❌ ChromaDB demo failed: {e}")
        print("💡 Make sure ChromaDB is installed: pip install chromadb")


def demonstrate_storage_switching():
    """Demonstrate switching between different storage types."""
    print("\n=== Storage Switching Demo ===")
    
    # Start with in-memory storage
    embedding_manager = EmbeddingManager(vector_storage_type="inmemory")
    
    # Create collection and add data
    collection_name = "test_collection"
    embedding_manager.create_collection(collection_name)
    
    # Store a test document
    doc_id = embedding_manager.store_embedding(
        collection_name,
        "This is a test document for storage switching",
        metadata={"test": True}
    )
    print(f"✅ Stored document in in-memory storage: {doc_id}")
    
    # Switch to ChromaDB (if available)
    try:
        success = embedding_manager.switch_vector_storage(
            "chroma",
            {"persist_directory": "./chroma_db"}
        )
        if success:
            print("✅ Switched to ChromaDB storage")
            
            # The same collection should be available
            collections = embedding_manager.list_collections()
            print(f"📁 Collections after switch: {collections}")
            
            # Try to retrieve the document (might not work due to different storage)
            if collection_name in collections:
                print("📄 Collection exists in new storage")
            
    except Exception as e:
        print(f"❌ Storage switching failed: {e}")


def demonstrate_crud_operations():
    """Demonstrate CRUD operations on vector storage."""
    print("\n=== CRUD Operations Demo ===")
    
    embedding_manager = EmbeddingManager(vector_storage_type="inmemory")
    collection_name = "crud_demo"
    embedding_manager.create_collection(collection_name)
    
    # CREATE
    print("📝 Creating documents...")
    doc1_id = embedding_manager.store_embedding(
        collection_name,
        "First document about Python programming",
        metadata={"topic": "python", "order": 1}
    )
    
    doc2_id = embedding_manager.store_embedding(
        collection_name,
        "Second document about machine learning",
        metadata={"topic": "ml", "order": 2}
    )
    
    print(f"✅ Created documents: {doc1_id}, {doc2_id}")
    
    # READ
    print("\n📖 Reading documents...")
    doc1 = embedding_manager.get_document(collection_name, doc1_id)
    if doc1:
        print(f"Document 1: {doc1.content}")
        print(f"Metadata: {doc1.metadata}")
    
    # UPDATE
    print("\n✏️ Updating document...")
    success = embedding_manager.update_document(
        collection_name, doc1_id,
        content="Updated first document about Python programming",
        metadata={"topic": "python", "order": 1, "updated": True}
    )
    print(f"✅ Update successful: {success}")
    
    # Verify update
    updated_doc = embedding_manager.get_document(collection_name, doc1_id)
    if updated_doc:
        print(f"Updated content: {updated_doc.content}")
        print(f"Updated metadata: {updated_doc.metadata}")
    
    # SEARCH
    print("\n🔍 Searching documents...")
    results = embedding_manager.search_similar(collection_name, "programming", limit=5)
    print(f"Found {len(results)} similar documents:")
    for content, score in results:
        print(f"Score: {score:.3f} - {content[:50]}...")
    
    # DELETE
    print("\n🗑️ Deleting document...")
    success = embedding_manager.delete_document(collection_name, doc2_id)
    print(f"✅ Delete successful: {success}")
    
    # Verify deletion
    deleted_doc = embedding_manager.get_document(collection_name, doc2_id)
    print(f"Document after deletion: {deleted_doc}")
    
    # Final count
    stats = embedding_manager.get_collection_stats(collection_name)
    print(f"📊 Final collection stats: {stats}")


def demonstrate_advanced_search():
    """Demonstrate advanced search features."""
    print("\n=== Advanced Search Demo ===")
    
    embedding_manager = EmbeddingManager(vector_storage_type="inmemory")
    collection_name = "advanced_search"
    embedding_manager.create_collection(collection_name)
    
    # Store documents with different metadata
    documents = [
        {
            "content": "Python web development with Django framework",
            "metadata": {"language": "python", "framework": "django", "year": 2023}
        },
        {
            "content": "Python web development with Flask framework",
            "metadata": {"language": "python", "framework": "flask", "year": 2023}
        },
        {
            "content": "JavaScript web development with React framework",
            "metadata": {"language": "javascript", "framework": "react", "year": 2023}
        },
        {
            "content": "Python data analysis with pandas library",
            "metadata": {"language": "python", "library": "pandas", "year": 2022}
        },
        {
            "content": "JavaScript data visualization with D3.js",
            "metadata": {"language": "javascript", "library": "d3", "year": 2022}
        }
    ]
    
    doc_ids = embedding_manager.store_batch(collection_name, documents)
    print(f"✅ Stored {len(doc_ids)} documents")
    
    # Search with metadata filter
    print("\n🔍 Searching for 'web development' with Python filter:")
    results = embedding_manager.search_similar(
        collection_name, 
        "web development", 
        limit=5,
        filter_metadata={"language": "python"}
    )
    
    for content, score in results:
        print(f"Score: {score:.3f} - {content}")
    
    # Search with year filter
    print("\n🔍 Searching for 'data' with 2022 year filter:")
    results = embedding_manager.search_similar(
        collection_name, 
        "data", 
        limit=5,
        filter_metadata={"year": 2022}
    )
    
    for content, score in results:
        print(f"Score: {score:.3f} - {content}")


def main():
    """Main function to run all demonstrations."""
    print("Vector Storage Examples")
    print("=" * 50)
    
    # Basic CRUD operations
    demonstrate_crud_operations()
    
    # In-memory storage demo
    demonstrate_inmemory_storage()
    
    # ChromaDB demo (if available)
    demonstrate_chroma_storage()
    
    # Storage switching demo
    demonstrate_storage_switching()
    
    # Advanced search demo
    demonstrate_advanced_search()
    
    print("\n🎉 All demonstrations completed!")
    print("\n💡 Tips:")
    print("   - In-memory storage is great for testing")
    print("   - ChromaDB is good for local development")
    print("   - Pinecone is ideal for production scale")
    print("   - You can easily switch between storage types")
    print("   - Metadata filtering enables powerful queries")


if __name__ == "__main__":
    main() 