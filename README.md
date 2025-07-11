# Project Requirements: Code Module Embedding Prototype

## Overview
This prototype will:
- Read code from a source code repository.
- Generate embeddings for various modules of the code.
- Store and manage project/module/code structure in a database.
- Provide APIs to manage project/module/code data and generate embeddings for code blocks.
- Extract code blocks (functions) from Python files for embedding.
- Use FastAPI for the backend.

## Database Structure
- **Project**
  - `id` (Primary Key)
  - `name`
- **Module**
  - `id` (Primary Key)
  - `project_id` (Foreign Key)
  - `name`
- **CodeDirectory**
  - `id` (Primary Key)
  - `module_id` (Foreign Key)
  - `path`
- **CodeFile**
  - `id` (Primary Key)
  - `module_id` (Foreign Key)
  - `path`
- **CodeBlock**
  - `id` (Primary Key)
  - `file_id` (Foreign Key)
  - `name` (e.g., function name)
  - `code` (text)
  - `embedding` (vector or serialized)

## API Endpoints
- **Project Management**
  - `POST /projects/` : Create a new project
  - `GET /projects/` : List all projects
  - `GET /projects/{project_id}` : Get project details

- **Module Management**
  - `POST /modules/` : Create a new module
  - `GET /modules/` : List all modules
  - `GET /modules/{module_id}` : Get module details

- **Code Directory Management**
  - `POST /directories/` : Add a code directory to a module
  - `GET /directories/` : List all code directories

- **Code File Management**
  - `POST /files/` : Add a code file to a module
  - `GET /files/` : List all code files

- **Embedding & Code Block Extraction**
  - `POST /embeddings/generate/` : Generate embeddings for all code blocks in a file/module
  - `GET /blocks/` : List all code blocks (optionally filter by file/module)

## Code Block Extraction
- For Python files, code blocks are defined as individual functions within a file.
- Extraction logic will parse Python files and extract each function as a code block.

## Tech Stack
- **Backend:** FastAPI
- **Database:** SQLite (for prototype)
- **ORM:** SQLAlchemy
- **Embeddings:** Placeholder (can use OpenAI, HuggingFace, or mock for prototype)

---

Development will proceed by first setting up the database models and FastAPI structure, then implementing the API endpoints, and finally adding code block extraction and embedding generation. 


For story point fine tuning - https://arxiv.org/abs/1609.00489