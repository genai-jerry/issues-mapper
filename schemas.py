from pydantic import BaseModel
from typing import List, Optional

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