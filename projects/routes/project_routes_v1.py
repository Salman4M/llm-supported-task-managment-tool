from fastapi import APIRouter, HTTPException, Depends, Request, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import httpx
import os
from core.database import get_db
from core.database import SessionLocal

from users.models.models_v1 import User
from users.utils.enum import UserRole
from projects.models.models_v1 import Project
from projects.schemas.project_schemas_v1 import *
from projects.repositories.project_repositories_v1 import ProjectRepository
from core.authentication import get_current_user


router = APIRouter(prefix='/api')

# Project endpoints
@router.get('/projects/', response_model=list[ProjectSchema], status_code=status.HTTP_200_OK)
def get_project_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = ProjectRepository(db)
    return repo.get_active_projects(skip, limit)


@router.get('/projects/{project_id}/', response_model=ProjectDetailSchema, status_code=status.HTTP_200_OK)
def get_project_detail(project_id: UUID, db: Session = Depends(get_db)):
    repo = ProjectRepository(db)
    project = repo.get_active_project(project_id)
    return project


# @router.post("/projects/create/", response_model=ProjectDetailSchema, status_code=status.HTTP_201_CREATED)
# def create_project(project: ProjectCreateSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     if current_user.role != UserRole.project_owner:
#         raise HTTPException(status_code=403, detail='You do not have permission')
    
#     repo = ProjectRepository(db)
#     return repo.create_project(data=project, created_by=current_user.id)


# @router.patch("/projects/update/{project_id}/", response_model=ProjectDetailSchema, status_code=status.HTTP_200_OK)
# def update_project(project_id: UUID, project: ProjectUpdateSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     repo = ProjectRepository(db)
#     db_project = repo.get_active_project(project_id)
#     if not db_project:
#         raise HTTPException(status_code=404, detail='Project not found')
    
#     if current_user.role not in [UserRole.project_owner, UserRole.team_lead]:
#         raise HTTPException(status_code=403, detail='You do not have permission')
    
#     return repo.update_project(project_id, project)


# @router.delete("/projects/{project_id}/", status_code=status.HTTP_204_NO_CONTENT)
# def delete_project(project_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     repo = ProjectRepository(db)
#     project = repo.get_active_project(project_id)
#     if project.created_by != current_user.id:
#         raise HTTPException(status_code=403, detail='You do not have permission')
    
#     repo.soft_delete(project_id)
