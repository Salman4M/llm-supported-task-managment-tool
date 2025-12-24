from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from uuid import UUID

from projects.models.models_v1 import Task, Project
from projects.schemas.task_schemas_v1 import TaskCreateSchema, TaskUpdateSchema


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, data: TaskCreateSchema, project_id: UUID) -> Task:
        try:
            task_data = data.dict(exclude_unset=True)
            task_data["project_id"] = project_id
            
            new_task = Task(**task_data)
            self.db.add(new_task)
            self.db.commit()
            self.db.refresh(new_task)
            return new_task
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def get_task_by_id(self, task_id: int) -> Task:
        task = (
            self.db.query(Task)
            .options(
                joinedload(Task.subtasks),
                joinedload(Task.assigned_user),
                joinedload(Task.project)
            )
            .filter(Task.id == task_id)
            .first()
        )
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task

    def get_tasks_by_project(self, project_id: UUID, skip: int = 0, limit: int = 100) -> list[Task]:
        return (
            self.db.query(Task)
            .options(
                joinedload(Task.subtasks),
                joinedload(Task.assigned_user)
            )
            .filter(
                Task.project_id == project_id,
                Task.parent_id.is_(None)  # Only parent tasks
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_subtasks(self, parent_task_id: int) -> list[Task]:
        return (
            self.db.query(Task)
            .options(joinedload(Task.assigned_user))
            .filter(Task.parent_id == parent_task_id)
            .all()
        )

    def update_task(self, task_id: int, data: TaskUpdateSchema) -> Task:
        task = self.get_task_by_id(task_id)
        
        try:
            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(task, key, value)
            
            self.db.commit()
            self.db.refresh(task)
            return task
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def assign_task(self, task_id: int, user_id: UUID) -> Task:
        task = self.get_task_by_id(task_id)
        
        try:
            task.assigned_to = user_id
            self.db.commit()
            self.db.refresh(task)
            return task
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def update_task_status(self, task_id: int, status: str) -> Task:
        task = self.get_task_by_id(task_id)
        
        try:
            from projects.utils.enum import Status
            task.status = Status[status]
            self.db.commit()
            self.db.refresh(task)
            return task
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        
        try:
            self.db.query(Task).filter(Task.parent_id == task_id).delete()
            
            self.db.delete(task)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def check_project_access(self, project_id: UUID, user_id: UUID) -> bool:
        project = (
            self.db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )
        
        if not project:
            return False
        
        if project.created_by == user_id:
            return True
        
        if project.team:
            team_member_ids = [member.id for member in project.team.team_members]
            if user_id in team_member_ids:
                return True
        
        return False