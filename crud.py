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