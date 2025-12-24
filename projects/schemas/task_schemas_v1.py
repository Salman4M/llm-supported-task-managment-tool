from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from projects.utils.enum import Status


class TaskBaseSchema(BaseModel):
    title: str
    project_id: UUID
    description: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskCreateSchema(TaskBaseSchema):
    assigned_to: Optional[UUID] = None
    parent_id: Optional[int] = None  # If creating a subtask


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    deadline: Optional[datetime] = None
    status: Optional[Status] = None


class TaskAssignSchema(BaseModel):
    user_id: UUID


class TaskStatusUpdateSchema(BaseModel):
    status: Status


class SubtaskSchema(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: Status
    assigned_to: Optional[UUID]
    deadline: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TaskResponseSchema(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: Status
    assigned_to: Optional[UUID]
    project_id: UUID
    parent_id: Optional[int]
    deadline: Optional[datetime]
    created_at: datetime
    subtasks: List[SubtaskSchema] = []

    class Config:
        from_attributes = True


class TaskListSchema(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: Status
    assigned_to: Optional[UUID]
    project_id: UUID
    deadline: Optional[datetime]
    created_at: datetime
    subtask_count: int = 0

    class Config:
        from_attributes = True