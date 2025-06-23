from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
import crud, schemas
from deps import get_db
from typing import List, Optional
from embedding_utils import extract_python_functions, mock_generate_embedding
from background_processor import processor

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

# Background Processing Job Endpoints
@router.post("/jobs/start/", response_model=schemas.ProcessingJob)
async def start_processing_job(job: schemas.ProcessingJobCreate, db: Session = Depends(get_db)):
    """Start a background processing job for a directory."""
    # Create the job record
    db_job = crud.create_processing_job(db, job)
    
    # Start the background processing
    await processor.start_processing_job(db_job.id)
    
    return db_job

@router.get("/jobs/", response_model=List[schemas.ProcessingJob])
def list_processing_jobs(db: Session = Depends(get_db)):
    """List all processing jobs."""
    return crud.get_processing_jobs(db)

@router.get("/jobs/{job_id}", response_model=schemas.ProcessingJob)
def get_processing_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific processing job with its progress."""
    job = crud.get_processing_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/jobs/{job_id}/resume/")
async def resume_processing_job(job_id: int, db: Session = Depends(get_db)):
    """Resume a failed or incomplete processing job."""
    job = crud.get_processing_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == "completed":
        raise HTTPException(status_code=400, detail="Job is already completed")
    
    # Resume the job
    await processor.start_processing_job(job_id)
    
    return {"message": f"Job {job_id} resumed successfully"}

@router.get("/jobs/{job_id}/tasks/", response_model=List[schemas.ProcessingTask])
def get_processing_tasks(job_id: int, db: Session = Depends(get_db)):
    """Get all tasks for a specific job."""
    return crud.get_processing_tasks(db, job_id=job_id)

@router.post("/jobs/resume-all/")
async def resume_all_incomplete_jobs(db: Session = Depends(get_db)):
    """Resume all incomplete jobs (useful for server restart)."""
    incomplete_jobs = crud.get_incomplete_jobs(db)
    resumed_count = 0
    
    for job in incomplete_jobs:
        await processor.start_processing_job(job.id)
        resumed_count += 1
    
    return {"message": f"Resumed {resumed_count} incomplete jobs"} 