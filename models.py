from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from db import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    modules = relationship("Module", back_populates="project")

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