from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import crud, schemas
from deps import get_db
from typing import List, Optional
from embedding_utils import extract_python_functions, mock_generate_embedding

router = APIRouter()

# Project Endpoints
@router.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, project)

@router.get("/projects/", response_model=List[schemas.Project])
def list_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)

@router.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# Module Endpoints
@router.post("/modules/", response_model=schemas.Module)
def create_module(module: schemas.ModuleCreate, db: Session = Depends(get_db)):
    return crud.create_module(db, module)

@router.get("/modules/", response_model=List[schemas.Module])
def list_modules(db: Session = Depends(get_db)):
    return crud.get_modules(db)

@router.get("/modules/{module_id}", response_model=schemas.Module)
def get_module(module_id: int, db: Session = Depends(get_db)):
    module = crud.get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

# CodeDirectory Endpoints
@router.post("/directories/", response_model=schemas.CodeDirectory)
def create_directory(directory: schemas.CodeDirectoryCreate, db: Session = Depends(get_db)):
    return crud.create_directory(db, directory)

@router.get("/directories/", response_model=List[schemas.CodeDirectory])
def list_directories(db: Session = Depends(get_db)):
    return crud.get_directories(db)

# CodeFile Endpoints
@router.post("/files/", response_model=schemas.CodeFile)
def create_file(file: schemas.CodeFileCreate, db: Session = Depends(get_db)):
    return crud.create_file(db, file)

@router.get("/files/", response_model=List[schemas.CodeFile])
def list_files(db: Session = Depends(get_db)):
    return crud.get_files(db)

# CodeBlock Endpoints
@router.get("/blocks/", response_model=List[schemas.CodeBlock])
def list_blocks(file_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_code_blocks(db, file_id=file_id)

# Embedding & Code Block Extraction Endpoint
@router.post("/embeddings/generate/")
def generate_embeddings(file_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    source_code = file.file.read().decode("utf-8")
    functions = extract_python_functions(source_code)
    blocks = []
    for func in functions:
        embedding = mock_generate_embedding(func['code'])
        block_in = schemas.CodeBlockCreate(
            name=func['name'], code=func['code'], file_id=file_id, embedding=embedding
        )
        block = crud.create_code_block(db, block_in)
        blocks.append(block)
    return blocks 