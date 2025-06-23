import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import crud, models
from embedding_utils import extract_python_functions, mock_generate_embedding
from db import SessionLocal

class BackgroundProcessor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_jobs = set()

    async def start_processing_job(self, job_id: int):
        """Start processing a job asynchronously."""
        if job_id in self.running_jobs:
            return {"message": "Job already running"}
        
        self.running_jobs.add(job_id)
        try:
            await self._process_job(job_id)
        finally:
            self.running_jobs.discard(job_id)

    async def _process_job(self, job_id: int):
        """Process a job by traversing directory and processing files."""
        db = SessionLocal()
        try:
            # Get job details
            job = crud.get_processing_job(db, job_id)
            if not job:
                return
            
            # Update job status to running
            crud.update_job_status(db, job_id, "running")
            
            # Get all Python files in the directory
            python_files = self._get_python_files(job.directory)
            
            # Create tasks for all functions in all files
            total_functions = 0
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    functions = extract_python_functions(source_code)
                    total_functions += len(functions)
                    
                    # Create tasks for each function
                    for func in functions:
                        task = crud.create_processing_task(db, models.ProcessingTaskCreate(
                            job_id=job_id,
                            file_path=file_path,
                            function_name=func['name']
                        ))
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
            
            # Update job with total counts
            crud.update_job_status(db, job_id, "running", 
                                 total_files=len(python_files),
                                 total_functions=total_functions)
            
            # Process files in parallel
            await self._process_files_parallel(db, job_id, python_files)
            
            # Mark job as completed
            crud.update_job_status(db, job_id, "completed")
            
        except Exception as e:
            crud.update_job_status(db, job_id, "failed", error_message=str(e))
        finally:
            db.close()

    def _get_python_files(self, directory: str) -> List[str]:
        """Recursively get all Python files in a directory."""
        python_files = []
        for root, dirs, files in os.walk(directory):
            # Skip common directories that shouldn't be processed
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files

    async def _process_files_parallel(self, db: Session, job_id: int, python_files: List[str]):
        """Process multiple files in parallel."""
        # Create tasks for processing each file
        tasks = []
        for file_path in python_files:
            task = asyncio.create_task(self._process_single_file(db, job_id, file_path))
            tasks.append(task)
        
        # Wait for all files to be processed
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_single_file(self, db: Session, job_id: int, file_path: str):
        """Process a single Python file and its functions."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            functions = extract_python_functions(source_code)
            
            # Process functions in parallel using thread pool
            loop = asyncio.get_event_loop()
            tasks = []
            for func in functions:
                task = loop.run_in_executor(
                    self.executor, 
                    self._process_function, 
                    db, job_id, file_path, func
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    def _process_function(self, db: Session, job_id: int, file_path: str, func: Dict):
        """Process a single function and generate embedding."""
        try:
            # Check if this function was already processed
            existing_task = crud.get_task_by_file_and_function(db, job_id, file_path, func['name'])
            if existing_task and existing_task.status == "completed":
                return
            
            # Generate embedding
            embedding = mock_generate_embedding(func['code'])
            
            # Create or update code block
            # First, ensure the file exists in the database
            file_record = db.query(models.CodeFile).filter(
                models.CodeFile.path == file_path
            ).first()
            
            if not file_record:
                # Create file record if it doesn't exist
                file_record = models.CodeFile(path=file_path, module_id=1)  # Default module
                db.add(file_record)
                db.commit()
                db.refresh(file_record)
            
            # Create code block
            code_block = models.CodeBlock(
                name=func['name'],
                code=func['code'],
                file_id=file_record.id,
                embedding=embedding
            )
            db.add(code_block)
            
            # Update task status
            if existing_task:
                crud.update_task_status(db, existing_task.id, "completed")
            else:
                crud.create_processing_task(db, models.ProcessingTaskCreate(
                    job_id=job_id,
                    file_path=file_path,
                    function_name=func['name'],
                    status="completed"
                ))
            
            db.commit()
            
        except Exception as e:
            # Update task status to failed
            existing_task = crud.get_task_by_file_and_function(db, job_id, file_path, func['name'])
            if existing_task:
                crud.update_task_status(db, existing_task.id, "failed", str(e))
            else:
                crud.create_processing_task(db, models.ProcessingTaskCreate(
                    job_id=job_id,
                    file_path=file_path,
                    function_name=func['name'],
                    status="failed",
                    error_message=str(e)
                ))
            db.commit()

    async def resume_incomplete_jobs(self):
        """Resume any incomplete jobs on server startup."""
        db = SessionLocal()
        try:
            incomplete_jobs = crud.get_incomplete_jobs(db)
            for job in incomplete_jobs:
                print(f"Resuming job {job.id} for directory {job.directory}")
                await self.start_processing_job(job.id)
        finally:
            db.close()

# Global processor instance
processor = BackgroundProcessor() 