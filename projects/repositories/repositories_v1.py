from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from fastapi import HTTPException
from .base import BaseRepository

from models.models_v1 import Project 
from schemas.schemas_v1 import ProjectCreateSchema, ProjectUpdateSchema


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_active_project(self, id: UUID) -> Project:
        project = self.db_session.query(Project).filter(
            Project.id == id,
            Project.is_active == True
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail='Project not found')
        
        return project

    def get_active_projects(self, skip: int = 0, limit: int = 10) -> list[Project]:
         return (self.db_session.query(Project).filter(Project.is_active == True).offset(skip).limit(limit).all())
    
    def create_project(self, data: ProjectCreateSchema, created_by: UUID) -> Project:
        try:
            project_data = data.dict(exclude_unset=True)
            project_data["created_by"] = created_by
            db_project = self.create(project_data)
            return db_project
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
    
    def update_project(self, id: UUID, data: ProjectUpdateSchema) -> Project:
        project = self.get(id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        try:
            update_data = data.dict(exclude_unset=True)
            updated_project = self.update(id, update_data)
            return updated_project
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def soft_delete(self, id: UUID) -> bool:
        project = self.get(id)
        if not project:
            raise HTTPException(status_code=404, detail='Project not found')
        
        try:
            project.is_active = False
            self.db_session.commit()
            return True
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=400, detail=str(e))