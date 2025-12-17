from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from fastapi import HTTPException
from .base import BaseRepository
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

from projects.models.models_v1 import Project 
from users.models.models_v1 import User
from teams.models.models_v1 import Team
from projects.schemas.project_schemas_v1 import ProjectCreateSchema, ProjectUpdateSchema


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_active_project(self, user_id: UUID, id: UUID) -> Project:
        project = (
            self.db_session.query(Project)
            .options(joinedload(Project.team).joinedload(Team.team_members))
            .filter(
                Project.id == id,
                Project.is_active.is_(True),
                or_(
                    Project.created_by == user_id,
                    Project.team.has(Team.team_members.any(User.id == user_id))
                )
            )
            .first()
        )

        if not project:
            raise HTTPException(status_code=404, detail='Project not found or access denied')
        
        return project


    def get_active_projects(self, user_id: UUID, skip: int = 0, limit: int = 10) -> list[Project]:
        return (
            self.db_session.query(Project)
            .options(joinedload(Project.team).joinedload(Team.team_members))
            .filter(
                Project.is_active.is_(True),
                or_(
                    Project.created_by == user_id,
                    Project.team.has(Team.team_members.any(User.id == user_id))
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    

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