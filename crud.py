from sqlalchemy.orm import Session
import models, schemas

# Project CRUD

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(name=project.name)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects(db: Session):
    return db.query(models.Project).all()

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

# Module CRUD

def create_module(db: Session, module: schemas.ModuleCreate):
    db_module = models.Module(name=module.name, project_id=module.project_id)
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

def get_modules(db: Session):
    return db.query(models.Module).all()

def get_module(db: Session, module_id: int):
    return db.query(models.Module).filter(models.Module.id == module_id).first()

# CodeDirectory CRUD

def create_directory(db: Session, directory: schemas.CodeDirectoryCreate):
    db_directory = models.CodeDirectory(path=directory.path, module_id=directory.module_id)
    db.add(db_directory)
    db.commit()
    db.refresh(db_directory)
    return db_directory

def get_directories(db: Session):
    return db.query(models.CodeDirectory).all()

# CodeFile CRUD

def create_file(db: Session, file: schemas.CodeFileCreate):
    db_file = models.CodeFile(path=file.path, module_id=file.module_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_files(db: Session):
    return db.query(models.CodeFile).all()

# CodeBlock CRUD

def create_code_block(db: Session, block: schemas.CodeBlockCreate):
    db_block = models.CodeBlock(
        name=block.name, code=block.code, file_id=block.file_id, embedding=block.embedding
    )
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block

def get_code_blocks(db: Session, file_id: int = None):
    query = db.query(models.CodeBlock)
    if file_id:
        query = query.filter(models.CodeBlock.file_id == file_id)
    return query.all()

# ProcessingJob CRUD

def create_processing_job(db: Session, job: schemas.ProcessingJobCreate):
    db_job = models.ProcessingJob(
        project_id=job.project_id,
        directory=job.directory
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_processing_job(db: Session, job_id: int):
    return db.query(models.ProcessingJob).filter(models.ProcessingJob.id == job_id).first()

def get_processing_jobs(db: Session):
    return db.query(models.ProcessingJob).all()

def get_incomplete_jobs(db: Session):
    """Get jobs that are pending or running for resuming on server restart."""
    return db.query(models.ProcessingJob).filter(
        models.ProcessingJob.status.in_(["pending", "running"])
    ).all()

def update_job_status(db: Session, job_id: int, status: str, **kwargs):
    """Update job status and other fields."""
    db_job = get_processing_job(db, job_id)
    if db_job:
        db_job.status = status
        for key, value in kwargs.items():
            if hasattr(db_job, key):
                setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
    return db_job

def update_job_progress(db: Session, job_id: int, processed_files: int = None, processed_functions: int = None):
    """Update job progress counters."""
    db_job = get_processing_job(db, job_id)
    if db_job:
        if processed_files is not None:
            db_job.processed_files = processed_files
        if processed_functions is not None:
            db_job.processed_functions = processed_functions
        db.commit()
        db.refresh(db_job)
    return db_job

# ProcessingTask CRUD

def create_processing_task(db: Session, task: schemas.ProcessingTaskCreate):
    db_task = models.ProcessingTask(
        job_id=task.job_id,
        file_path=task.file_path,
        function_name=task.function_name,
        status=task.status,
        error_message=task.error_message
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_processing_tasks(db: Session, job_id: int = None):
    query = db.query(models.ProcessingTask)
    if job_id:
        query = query.filter(models.ProcessingTask.job_id == job_id)
    return query.all()

def get_pending_tasks(db: Session, job_id: int):
    """Get pending tasks for a specific job."""
    return db.query(models.ProcessingTask).filter(
        models.ProcessingTask.job_id == job_id,
        models.ProcessingTask.status == "pending"
    ).all()

def update_task_status(db: Session, task_id: int, status: str, error_message: str = None):
    """Update task status and error message."""
    db_task = db.query(models.ProcessingTask).filter(models.ProcessingTask.id == task_id).first()
    if db_task:
        db_task.status = status
        if error_message:
            db_task.error_message = error_message
        db.commit()
        db.refresh(db_task)
    return db_task

def get_task_by_file_and_function(db: Session, job_id: int, file_path: str, function_name: str):
    """Get a specific task by job_id, file_path, and function_name."""
    return db.query(models.ProcessingTask).filter(
        models.ProcessingTask.job_id == job_id,
        models.ProcessingTask.file_path == file_path,
        models.ProcessingTask.function_name == function_name
    ).first() 