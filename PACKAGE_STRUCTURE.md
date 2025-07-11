# Package Structure Documentation

This document describes the reorganized package structure for the Issues Manager MVP project.

## Overview

The code has been reorganized into logical packages to improve maintainability, separation of concerns, and code organization.

## Package Structure

```
mvp/
├── api/                    # API and request processing
│   ├── __init__.py
│   ├── routes.py          # FastAPI routes and endpoints
│   └── dependencies.py    # API dependencies (database sessions, etc.)
│
├── core/                   # Core application logic
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy database models
│   ├── schemas.py         # Pydantic schemas for API
│   ├── database.py        # Database connection and setup
│   ├── crud.py           # Database CRUD operations
│   └── background_processor.py  # Background job processing
│
├── embeddings/             # Embedding generation and management
│   ├── __init__.py
│   ├── embedding_manager.py    # Main embedding management
│   ├── embedding_config.py     # Embedding configuration
│   └── embedding_utils.py      # Utility functions for code processing
│
├── vector_storage/         # Vector database management
│   ├── __init__.py
│   ├── vector_manager.py      # Vector storage management
│   ├── vector_config.py       # Vector storage configuration
│   ├── vector_models.py       # Vector data models
│   └── vector_utils.py        # Vector storage utilities
│
├── llm/                    # Language model interactions
│   ├── __init__.py
│   ├── llm_manager.py         # LLM chat and text generation
│   └── llm_config.py          # LLM configuration
│
├── tests/                  # All test code
│   ├── __init__.py
│   ├── test_embedding_storage.py
│   ├── embedding_with_vector_db_example.py
│   ├── vector_storage_example.py
│   ├── llm_example.py
│   ├── openrouter_example.py
│   └── discover_openrouter_models.py
│
├── static/                 # Static web assets
│   ├── app.js
│   └── style.css
│
├── templates/              # HTML templates
│   └── index.html
│
├── chroma_db/              # ChromaDB data directory
├── main.py                 # FastAPI application entry point
├── vector_db_dashboard.py  # Streamlit vector dashboard
└── requirements.txt        # Python dependencies
```

## Package Descriptions

### API Package (`api/`)
Handles all HTTP request processing and API endpoints.

- **routes.py**: Contains all FastAPI route definitions for projects, modules, files, embeddings, and background jobs
- **dependencies.py**: Provides dependency injection for database sessions and other API dependencies

### Core Package (`core/`)
Contains the core business logic and data models.

- **models.py**: SQLAlchemy ORM models for database tables
- **schemas.py**: Pydantic schemas for request/response validation
- **database.py**: Database connection setup and session management
- **crud.py**: Database CRUD operations for all entities
- **background_processor.py**: Background job processing for code analysis

### Embeddings Package (`embeddings/`)
Manages code embedding generation and processing.

- **embedding_manager.py**: Main class for generating and managing embeddings
- **embedding_config.py**: Configuration for embedding providers and models
- **embedding_utils.py**: Utility functions for code extraction and processing

### Vector Storage Package (`vector_storage/`)
Handles vector database operations and storage.

- **vector_manager.py**: Main vector storage management with support for multiple backends
- **vector_config.py**: Configuration for vector storage backends
- **vector_models.py**: Data models for vector documents and search results
- **vector_utils.py**: Utility functions for vector operations

### LLM Package (`llm/`)
Manages language model interactions for text generation and analysis.

- **llm_manager.py**: Main class for LLM chat and text generation
- **llm_config.py**: Configuration for LLM providers and models

### Tests Package (`tests/`)
Contains all test code and examples.

- **test_embedding_storage.py**: Tests for embedding storage functionality
- **embedding_with_vector_db_example.py**: Example of using embeddings with vector database
- **vector_storage_example.py**: Example of vector storage operations
- **llm_example.py**: Example of LLM interactions
- **openrouter_example.py**: Example of OpenRouter integration
- **discover_openrouter_models.py**: Utility to discover available OpenRouter models

## Key Benefits of Reorganization

1. **Separation of Concerns**: Each package has a specific responsibility
2. **Improved Maintainability**: Related code is grouped together
3. **Better Testability**: Tests are organized in their own package
4. **Clear Dependencies**: Package dependencies are explicit and manageable
5. **Scalability**: Easy to add new features to appropriate packages

## Usage Examples

### Using Embeddings
```python
from embeddings.embedding_manager import EmbeddingManager
from llm.llm_config import LLMConfig

config = LLMConfig()
config.set_embedding_config("openai", "text-embedding-ada-002", "your-api-key")

embedding_manager = EmbeddingManager(config)
embedding = embedding_manager.generate_embedding("def hello(): print('world')")
```

### Using Vector Storage
```python
from vector_storage.vector_manager import VectorStorageManager
from vector_storage.vector_models import VectorDocument

vector_manager = VectorStorageManager("chroma", {"persist_directory": "chroma_db"})
vector_manager.initialize()

document = VectorDocument(
    content="def hello(): print('world')",
    embedding=[0.1, 0.2, ...],
    metadata={"type": "function"}
)
vector_manager.insert_documents("code_functions", [document])
```

### Using LLM
```python
from llm.llm_manager import LLMManager
from llm.llm_config import LLMConfig

config = LLMConfig()
config.set_chat_config("openai", "gpt-3.5-turbo", "your-api-key")

llm_manager = LLMManager(config)
response = llm_manager.analyze_code("def hello(): print('world')")
```

## Migration Notes

- All imports have been updated to use the new package structure
- The main application entry point (`main.py`) has been updated
- The vector dashboard has been updated to use the new imports
- All test files have been moved to the `tests/` package

## Running the Application

The application can still be started using the same commands:

```bash
# Start the main FastAPI application
./start_server.sh

# Start the vector dashboard
cd mvp
streamlit run vector_db_dashboard.py
``` 