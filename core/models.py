from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    modules = relationship("Module", back_populates="project")
    jobs = relationship("ProcessingJob", back_populates="project")

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="modules")
    directories = relationship("CodeDirectory", back_populates="module")
    files = relationship("CodeFile", back_populates="module")

class CodeDirectory(Base):
    __tablename__ = "code_directories"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String)
    module_id = Column(Integer, ForeignKey("modules.id"))
    module = relationship("Module", back_populates="directories")

class CodeFile(Base):
    __tablename__ = "code_files"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String)
    module_id = Column(Integer, ForeignKey("modules.id"))
    module = relationship("Module", back_populates="files")
    blocks = relationship("CodeBlock", back_populates="file")

class CodeBlock(Base):
    __tablename__ = "code_blocks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(Text)
    embedding = Column(Text)  # Store as JSON/text for prototype
    file_id = Column(Integer, ForeignKey("code_files.id"))
    file = relationship("CodeFile", back_populates="blocks")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    directory = Column(String)
    status = Column(String, default="pending")  # pending, running, completed, failed
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    total_functions = Column(Integer, default=0)
    processed_functions = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project = relationship("Project", back_populates="jobs")
    tasks = relationship("ProcessingTask", back_populates="job")

class ProcessingTask(Base):
    __tablename__ = "processing_tasks"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("processing_jobs.id"))
    file_path = Column(String)
    function_name = Column(String)
    status = Column(String, default="pending")  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    job = relationship("ProcessingJob", back_populates="tasks") 