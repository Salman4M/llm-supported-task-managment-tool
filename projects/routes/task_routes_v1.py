from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.authentication import get_current_user
from users.models.models_v1 import User
from users.utils.enum import UserRole
from projects.models.models_v1 import Task
from projects.schemas.task_schemas_v1 import (
    TaskCreateSchema,
    TaskUpdateSchema,
    TaskResponseSchema,
    TaskListSchema,
    TaskAssignSchema,
    TaskStatusUpdateSchema,
    SubtaskSchema
)
from projects.repositories.task_repositories_v1 import TaskRepository


router = APIRouter(
    prefix='/api',
    tags=['Tasks']
)

@router.post("/create/{project_id}", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: UUID,
    task: TaskCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.team_lead:
        raise HTTPException(
            status_code=403,
            detail="Only Team Lead can create tasks"
        )
    
    repo = TaskRepository(db)
    
    if not repo.check_project_access(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this project"
        )
    
    return repo.create_task(data=task, project_id=project_id)


@router.get("/project/{project_id}", response_model=List[TaskResponseSchema])
def get_tasks_by_project(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    
    if not repo.check_project_access(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this project"
        )
    
    tasks = repo.get_tasks_by_project(project_id, skip, limit)
    
    result = []
    for task in tasks:
        task_dict = TaskResponseSchema.from_orm(task).dict()
        task_dict['subtask_count'] = len(task.subtasks)
        result.append(task_dict)
    
    return tasks


@router.get("/{task_id}", response_model=TaskResponseSchema)
def get_task_details(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    repo = TaskRepository(db)
    task = repo.get_task_by_id(task_id)
    
    if not repo.check_project_access(task.project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        )
    
    return task


@router.patch("/{task_id}", response_model=TaskResponseSchema)
def update_task(
    task_id: int,
    task_update: TaskUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user.role != UserRole.team_lead:
        raise HTTPException(
            status_code=403,
            detail="Only Team Lead can update tasks"
        )
    
    repo = TaskRepository(db)
    task = repo.get_task_by_id(task_id)
    
    if not repo.check_project_access(task.project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        )
    
    return repo.update_task(task_id, task_update)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user.role != UserRole.team_lead:
        raise HTTPException(
            status_code=403,
            detail="Only Team Lead can delete tasks"
        )
    
    repo = TaskRepository(db)
    task = repo.get_task_by_id(task_id)
    
    if not repo.check_project_access(task.project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        )
    
    repo.delete_task(task_id)


@router.patch("/{task_id}/assign", response_model=TaskResponseSchema)
def assign_task(
    task_id: int,
    assignment: TaskAssignSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user.role not in [UserRole.team_lead, UserRole.project_owner]:
        raise HTTPException(
            status_code=403,
            detail="Only Team Lead or Project Owner can assign tasks"
        )
    
    repo = TaskRepository(db)
    task = repo.get_task_by_id(task_id)
    
    if not repo.check_project_access(task.project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        )
    
    return repo.assign_task(task_id, assignment.user_id)


@router.patch("/{task_id}/status", response_model=TaskResponseSchema)
def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user.role != UserRole.team_lead:
        raise HTTPException(
            status_code=403,
            detail="Only Team Lead can update task status"
        )
    
    repo = TaskRepository(db)
    task = repo.get_task_by_id(task_id)
    
    if not repo.check_project_access(task.project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        )
        
    if task.parent_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Use subtask status endpoint for subtasks"
        )
    
    return repo.update_task_status(task_id, status_update.status.value)


@router.patch("/{task_id}/subtasks/{subtask_id}/status", response_model=SubtaskSchema)
def update_subtask_status(
    task_id: int,
    subtask_id: int,
    status_update: TaskStatusUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)    
    parent_task = repo.get_task_by_id(task_id)
    
    if not repo.check_project_access(parent_task.project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        ) 
    subtask = repo.get_task_by_id(subtask_id)
    
    if subtask.parent_id != task_id:
        raise HTTPException(
            status_code=400,
            detail="This is not a subtask of the specified task"
        )
    
    if current_user.role == UserRole.team_member:
        if subtask.assigned_to != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own assigned subtasks"
            )
    elif current_user.role not in [UserRole.team_lead, UserRole.project_owner]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this subtask"
        )
    
    return repo.update_task_status(subtask_id, status_update.status.value)


@router.post("/{task_id}/subtasks", response_model=SubtaskSchema, status_code=status.HTTP_201_CREATED)
def create_subtask(
    task_id: int,
    subtask: TaskCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user.role != UserRole.team_lead:
        raise HTTPException(
            status_code=403,
            detail="Only Team Lead can create subtasks"
        )
    
    repo = TaskRepository(db)
    parent_task = repo.get_task_by_id(task_id)
    
    if not repo.check_project_access(parent_task.project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        )
    subtask.parent_id = task_id
    
    return repo.create_task(data=subtask, project_id=parent_task.project_id)


@router.get("/{task_id}/subtasks", response_model=List[SubtaskSchema])
def get_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    parent_task = repo.get_task_by_id(task_id)
    
    if not repo.check_project_access(parent_task.project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        )
    
    return repo.get_subtasks(task_id)