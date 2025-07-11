# Vector Storage Guide

This guide explains how to use the vector storage functionality in the Issues Manager MVP.

## Overview

The vector storage system provides a flexible abstraction layer for storing and searching embeddings. It supports multiple vector databases with a unified CRUD interface, allowing you to easily switch between different storage solutions.

## Features

- **Multiple Storage Backends**: In-memory, ChromaDB, Pinecone
- **Unified CRUD Interface**: Same API across all storage types
- **Easy Storage Switching**: Change storage backends without code changes
- **Metadata Filtering**: Advanced search with metadata filters
- **Batch Operations**: Efficient bulk operations
- **Collection Management**: Create, delete, and manage collections

## Quick Start

### 1. Basic Usage

```python
from llm import EmbeddingManager

# Create embedding manager with in-memory storage
manager = EmbeddingManager(vector_storage_type="inmemory")

# Create a collection
manager.create_collection("my_collection")

# Store a document
doc_id = manager.store_embedding(
    "my_collection", 
    "This is some content to store",
    metadata={"category": "example", "tags": ["test"]}
)

# Search for similar content
results = manager.search_similar("my_collection", "similar content", limit=5)
for content, score in results:
    print(f"Score: {score:.3f} - {content}")
```

### 2. ChromaDB Storage

```python
from llm import EmbeddingManager

# Create with ChromaDB storage
manager = EmbeddingManager(
    vector_storage_type="chroma",
    vector_storage_config={
        "persist_directory": "./chroma_db"
    }
)

# Use the same interface as in-memory storage
manager.create_collection("persistent_collection")
doc_id = manager.store_embedding("persistent_collection", "content")
```

### 3. Pinecone Storage

```python
from llm import EmbeddingManager

# Create with Pinecone storage
manager = EmbeddingManager(
    vector_storage_type="pinecone",
    vector_storage_config={
        "api_key": "your-pinecone-api-key",
        "environment": "us-west1-gcp"
    }
)

# Use the same interface
manager.create_collection("cloud_collection")
doc_id = manager.store_embedding("cloud_collection", "content")
```

## Storage Types

### In-Memory Storage
- **Use Case**: Testing, development, prototyping
- **Pros**: Fast, no setup required, immediate results
- **Cons**: No persistence, data lost on restart
- **Configuration**: None required

### ChromaDB Storage
- **Use Case**: Local development, small-scale production
- **Pros**: Persistent, local storage, good performance
- **Cons**: Limited scalability, local only
- **Configuration**:
  ```json
  {
    "persist_directory": "./chroma_db",
    "use_http_client": false
  }
  ```

### Pinecone Storage
- **Use Case**: Production, large-scale applications
- **Pros**: Scalable, cloud-based, high performance
- **Cons**: Requires API key, potential costs
- **Configuration**:
  ```json
  {
    "api_key": "your-pinecone-api-key",
    "environment": "us-west1-gcp"
  }
  ```

## CRUD Operations

### Create
```python
# Store single document
doc_id = manager.store_embedding(
    "collection_name",
    "content",
    metadata={"key": "value"}
)

# Store multiple documents
documents = [
    {"content": "doc1", "metadata": {"tag": "a"}},
    {"content": "doc2", "metadata": {"tag": "b"}}
]
doc_ids = manager.store_batch("collection_name", documents)
```

### Read
```python
# Get document by ID
doc = manager.get_document("collection_name", "doc_id")
if doc:
    print(f"Content: {doc.content}")
    print(f"Metadata: {doc.metadata}")
```

### Update
```python
# Update content and metadata
success = manager.update_document(
    "collection_name",
    "doc_id",
    content="updated content",
    metadata={"updated": True}
)

# Update only metadata
success = manager.update_document(
    "collection_name",
    "doc_id",
    metadata={"new_key": "new_value"}
)
```

### Delete
```python
# Delete document
success = manager.delete_document("collection_name", "doc_id")

# Clear entire collection
success = manager.clear_collection("collection_name")
```

## Search Operations

### Basic Search
```python
# Search for similar content
results = manager.search_similar(
    "collection_name",
    "query text",
    limit=10
)

for content, score in results:
    print(f"Similarity: {score:.3f}")
    print(f"Content: {content}")
```

### Advanced Search with Metadata Filtering
```python
# Search with metadata filter
results = manager.search_similar(
    "collection_name",
    "query text",
    limit=10,
    filter_metadata={
        "category": "python",
        "difficulty": "easy"
    }
)
```

### Complex Metadata Filters
```python
# Multiple filter conditions
results = manager.search_similar(
    "collection_name",
    "query text",
    filter_metadata={
        "language": "python",
        "year": 2023,
        "tags": ["web", "api"]
    }
)
```

## Collection Management

### Create Collection
```python
# Create with default dimension (1536)
manager.create_collection("my_collection")

# Create with custom dimension
manager.create_collection("my_collection", dimension=768)
```

### List Collections
```python
collections = manager.list_collections()
print(f"Available collections: {collections}")
```

### Delete Collection
```python
success = manager.delete_collection("my_collection")
```

### Collection Statistics
```python
stats = manager.get_collection_stats("my_collection")
print(f"Document count: {stats['document_count']}")
print(f"Storage type: {stats['storage_type']}")
```

## Storage Switching

You can easily switch between different storage types:

```python
# Start with in-memory storage
manager = EmbeddingManager(vector_storage_type="inmemory")

# Switch to ChromaDB
success = manager.switch_vector_storage(
    "chroma",
    {"persist_directory": "./chroma_db"}
)

# Switch to Pinecone
success = manager.switch_vector_storage(
    "pinecone",
    {"api_key": "key", "environment": "env"}
)
```

## Configuration

### Environment Variables
```bash
# Set default storage type
export VECTOR_STORAGE_TYPE="chroma"

# ChromaDB settings
export CHROMA_PERSIST_DIR="./chroma_db"

# Pinecone settings
export PINECONE_API_KEY="your-key"
export PINECONE_ENVIRONMENT="us-west1-gcp"
```

### Configuration File
See `vector_storage_config.json` for detailed configuration examples.

## Performance Optimization

### Batch Operations
```python
# Use batch operations for multiple documents
documents = [
    {"content": f"Document {i}", "metadata": {"index": i}}
    for i in range(1000)
]
doc_ids = manager.store_batch("collection_name", documents)
```

### Caching
The embedding manager includes built-in caching for embeddings:
```python
# Cache stats
cache_stats = manager.get_cache_stats()
print(f"Cache enabled: {cache_stats['enabled']}")
print(f"Cache size: {cache_stats['total_size_mb']} MB")
```

### Collection Optimization
```python
# Use appropriate dimensions for your embeddings
# OpenAI text-embedding-ada-002: 1536
# OpenAI text-embedding-3-small: 1536
# OpenAI text-embedding-3-large: 3072
manager.create_collection("optimized_collection", dimension=1536)
```

## Error Handling

### Storage Initialization
```python
try:
    manager = EmbeddingManager(vector_storage_type="pinecone")
    if not manager.vector_storage.initialized:
        print("Failed to initialize storage")
except Exception as e:
    print(f"Storage initialization error: {e}")
```

### Operation Errors
```python
try:
    doc_id = manager.store_embedding("collection", "content")
    if not doc_id:
        print("Failed to store document")
except Exception as e:
    print(f"Storage operation error: {e}")
```

## Use Cases

### Code Snippet Storage
```python
# Store code snippets with metadata
code_snippets = [
    {
        "content": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        "metadata": {
            "language": "python",
            "category": "algorithms",
            "difficulty": "easy",
            "tags": ["recursion", "math"]
        }
    }
]

doc_ids = manager.store_batch("code_snippets", code_snippets)

# Search for similar algorithms
results = manager.search_similar(
    "code_snippets",
    "recursive function",
    filter_metadata={"language": "python"}
)
```

### Issue Management
```python
# Store issue descriptions
issue = {
    "content": "User reports that the login button is not working on mobile devices",
    "metadata": {
        "status": "open",
        "priority": "high",
        "assignee": "frontend-team",
        "labels": ["bug", "mobile", "ui"]
    }
}

doc_id = manager.store_embedding("issues", issue["content"], issue["metadata"])

# Find similar issues
similar_issues = manager.search_similar(
    "issues",
    "mobile login problem",
    filter_metadata={"status": "open"}
)
```

### Documentation Search
```python
# Store documentation
docs = [
    {
        "content": "FastAPI is a modern web framework for building APIs with Python",
        "metadata": {
            "framework": "fastapi",
            "version": "0.100.0",
            "type": "introduction"
        }
    }
]

manager.store_batch("documentation", docs)

# Search documentation
results = manager.search_similar(
    "documentation",
    "web framework API",
    filter_metadata={"framework": "fastapi"}
)
```

## Troubleshooting

### Common Issues

1. **ChromaDB Import Error**
   ```bash
   pip install chromadb
   ```

2. **Pinecone Import Error**
   ```bash
   pip install pinecone-client
   ```

3. **Storage Initialization Failed**
   - Check API keys for cloud services
   - Verify network connectivity
   - Check storage directory permissions

4. **Search Returns No Results**
   - Verify collection exists
   - Check if documents were stored successfully
   - Try without metadata filters first

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check storage status
print(f"Storage initialized: {manager.vector_storage.initialized}")
print(f"Storage type: {manager.vector_storage.storage_type}")
```

## Examples

Run the example script to see all features in action:
```bash
python vector_storage_example.py
```

This will demonstrate:
- CRUD operations
- Different storage types
- Storage switching
- Advanced search features
- Performance optimization

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Local Storage**: Secure ChromaDB persistence directories
3. **Metadata**: Be careful with sensitive data in metadata
4. **Access Control**: Implement proper access control for production

## Next Steps

1. Choose the appropriate storage type for your use case
2. Set up configuration for your chosen storage
3. Create collections for your data types
4. Implement search functionality in your application
5. Monitor performance and optimize as needed 