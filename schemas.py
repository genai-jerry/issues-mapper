from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    class Config:
        orm_mode = True

class ModuleBase(BaseModel):
    name: str
    project_id: int

class ModuleCreate(ModuleBase):
    pass

class Module(ModuleBase):
    id: int
    class Config:
        orm_mode = True

class CodeDirectoryBase(BaseModel):
    path: str
    module_id: int

class CodeDirectoryCreate(CodeDirectoryBase):
    pass

class CodeDirectory(CodeDirectoryBase):
    id: int
    class Config:
        orm_mode = True

class CodeFileBase(BaseModel):
    path: str
    module_id: int

class CodeFileCreate(CodeFileBase):
    pass

class CodeFile(CodeFileBase):
    id: int
    class Config:
        orm_mode = True

class CodeBlockBase(BaseModel):
    name: str
    code: str
    file_id: int
    embedding: Optional[str] = None

class CodeBlockCreate(CodeBlockBase):
    pass

class CodeBlock(CodeBlockBase):
    id: int
    class Config:
        orm_mode = True

# ProcessingJob and ProcessingTask schemas
class ProcessingTaskBase(BaseModel):
    file_path: str
    function_name: str
    status: str = "pending"
    error_message: Optional[str] = None

class ProcessingTaskCreate(ProcessingTaskBase):
    job_id: int

class ProcessingTask(ProcessingTaskBase):
    id: int
    job_id: int
    class Config:
        orm_mode = True

class ProcessingJobBase(BaseModel):
    project_id: int
    directory: str

class ProcessingJobCreate(ProcessingJobBase):
    pass

class ProcessingJob(ProcessingJobBase):
    id: int
    status: str
    total_files: int
    processed_files: int
    total_functions: int
    processed_functions: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    tasks: List[ProcessingTask] = []
    class Config:
        orm_mode = True 