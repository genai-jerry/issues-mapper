# Embedding Storage with Vector Database

This document explains how to use the enhanced embedding functionality that automatically saves embeddings to vector databases.

## Overview

The `EmbeddingManager` now supports automatic storage of embeddings to vector databases (ChromaDB, Pinecone, or in-memory) when generating embeddings. This allows you to:

- Generate embeddings and store them in a vector database in one operation
- Search for similar content using semantic similarity
- Manage collections of embeddings
- Use different storage backends

## Quick Start

### 1. Basic Usage

```python
from llm.config import LLMConfig
from llm.embeddings import EmbeddingManager

# Setup configuration
config = LLMConfig()
config.embedding_provider = "openai"
config.embedding_model = "text-embedding-ada-002"
config.embedding_api_key = "your-api-key"

# Initialize with ChromaDB
embedding_manager = EmbeddingManager(
    config_instance=config,
    vector_storage_type="chroma",
    vector_storage_config={
        "persist_directory": "chroma_db"
    }
)

# Create a collection
embedding_manager.create_collection("documents", dimension=1536)

# Generate embedding and save to vector database
embedding = embedding_manager.generate_embedding(
    text="Your text here",
    save_to_vector_db=True,
    collection="documents",
    metadata={"source": "example", "category": "test"}
)
```

### 2. Batch Processing

```python
# Batch generate embeddings and save to vector database
texts = ["Text 1", "Text 2", "Text 3"]
metadata_list = [
    {"category": "a"},
    {"category": "b"},
    {"category": "c"}
]

embeddings = embedding_manager.batch_generate_embeddings(
    texts=texts,
    save_to_vector_db=True,
    collection="documents",
    metadata_list=metadata_list
)
```

### 3. Search Similar Content

```python
# Search for similar content
results = embedding_manager.search_similar(
    collection="documents",
    query="search query",
    limit=10,
    filter_metadata={"category": "a"}
)

for doc_id, similarity in results:
    doc = embedding_manager.get_document("documents", doc_id)
    print(f"Similarity: {similarity:.4f}")
    print(f"Content: {doc.content}")
    print(f"Metadata: {doc.metadata}")
```

## API Reference

### EmbeddingManager.generate_embedding()

```python
def generate_embedding(
    self, 
    text: str, 
    model: Optional[str] = None,
    save_to_vector_db: bool = False,
    collection: str = None,
    metadata: Dict[str, Any] = None
) -> List[float]
```

**Parameters:**
- `text`: Text to generate embedding for
- `model`: Optional model override
- `save_to_vector_db`: Whether to save to vector database
- `collection`: Collection name for vector storage
- `metadata`: Metadata to store with the embedding

**Returns:**
- `List[float]`: Embedding vector

### EmbeddingManager.batch_generate_embeddings()

```python
def batch_generate_embeddings(
    self,
    texts: List[str],
    model: Optional[str] = None,
    save_to_vector_db: bool = False,
    collection: str = None,
    metadata_list: List[Dict[str, Any]] = None
) -> List[List[float]]
```

**Parameters:**
- `texts`: List of texts to generate embeddings for
- `model`: Optional model override
- `save_to_vector_db`: Whether to save to vector database
- `collection`: Collection name for vector storage
- `metadata_list`: List of metadata dictionaries for each text

**Returns:**
- `List[List[float]]`: List of embedding vectors

## Vector Storage Backends

### ChromaDB (Recommended)

```python
embedding_manager = EmbeddingManager(
    vector_storage_type="chroma",
    vector_storage_config={
        "persist_directory": "chroma_db",
        "collection_name": "default"
    }
)
```

### In-Memory Storage

```python
embedding_manager = EmbeddingManager(
    vector_storage_type="inmemory"
)
```

### Pinecone

```python
embedding_manager = EmbeddingManager(
    vector_storage_type="pinecone",
    vector_storage_config={
        "api_key": "your-pinecone-api-key",
        "environment": "your-pinecone-environment"
    }
)
```

## Collection Management

### Create Collection

```python
embedding_manager.create_collection("my_collection", dimension=1536)
```

### List Collections

```python
collections = embedding_manager.list_collections()
print(collections)  # ['documents', 'my_collection']
```

### Get Collection Statistics

```python
stats = embedding_manager.get_collection_stats("my_collection")
print(stats)  # {'document_count': 10, 'dimension': 1536, ...}
```

### Delete Collection

```python
embedding_manager.delete_collection("my_collection")
```

### Clear Collection

```python
embedding_manager.clear_collection("my_collection")
```

## Document Management

### Get Document

```python
doc = embedding_manager.get_document("my_collection", "doc_id")
if doc:
    print(f"Content: {doc.content}")
    print(f"Metadata: {doc.metadata}")
```

### Update Document

```python
success = embedding_manager.update_document(
    collection="my_collection",
    document_id="doc_id",
    content="Updated content",
    metadata={"updated": True}
)
```

### Delete Document

```python
success = embedding_manager.delete_document("my_collection", "doc_id")
```

## Examples

### Example 1: Document Storage and Search

```python
# Store documents
documents = [
    "Python is a programming language",
    "Machine learning is a subset of AI",
    "Vector databases store embeddings"
]

for i, doc in enumerate(documents):
    embedding_manager.generate_embedding(
        text=doc,
        save_to_vector_db=True,
        collection="knowledge_base",
        metadata={"index": i, "category": "programming"}
    )

# Search for similar content
results = embedding_manager.search_similar(
    collection="knowledge_base",
    query="What is programming?",
    limit=3
)

for doc_id, similarity in results:
    doc = embedding_manager.get_document("knowledge_base", doc_id)
    print(f"Similarity: {similarity:.4f} - {doc.content}")
```

### Example 2: Filtered Search

```python
# Search with metadata filter
results = embedding_manager.search_similar(
    collection="knowledge_base",
    query="artificial intelligence",
    limit=5,
    filter_metadata={"category": "programming"}
)
```

## ChromaDB Management Scripts

The project includes shell scripts for managing ChromaDB:

### Start ChromaDB Server

```bash
# Start in persistent mode (local)
./start_chromadb.sh

# Start as server (remote access)
./start_chromadb.sh server
```

### Stop ChromaDB Server

```bash
./stop_chromadb.sh
```

### Check ChromaDB Status

```bash
./status_chromadb.sh
```

## Configuration

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# OpenRouter
export OPENROUTER_API_KEY="your-openrouter-api-key"

# ChromaDB (optional)
export CHROMA_HOST="localhost"
export CHROMA_PORT="8000"
```

### Configuration File

```python
config = LLMConfig()
config.embedding_provider = "openai"  # or "openrouter", "huggingface"
config.embedding_model = "text-embedding-ada-002"
config.embedding_api_key = "your-api-key"
config.enable_cache = True
config.cache_dir = "embedding_cache"
```

## Best Practices

1. **Use Collections**: Organize your embeddings into logical collections
2. **Add Metadata**: Include relevant metadata for filtering and organization
3. **Batch Processing**: Use batch methods for large datasets
4. **Error Handling**: Always handle exceptions when working with external APIs
5. **Caching**: Enable caching to avoid regenerating the same embeddings
6. **Backup**: Regularly backup your vector database data

## Troubleshooting

### Common Issues

1. **ChromaDB Connection Error**: Make sure ChromaDB is running and accessible
2. **API Key Issues**: Verify your API keys are correctly set
3. **Memory Issues**: Use persistent storage for large datasets
4. **Dimension Mismatch**: Ensure collection dimension matches your embedding model

### Debug Mode

Enable debug output by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing

Run the test script to verify functionality:

```bash
python mvp/test_embedding_storage.py
```

Or run the comprehensive example:

```bash
python mvp/embedding_with_vector_db_example.py
``` 