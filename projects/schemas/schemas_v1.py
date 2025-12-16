from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum

from projects.utils.enum import Status


class ProjectSchema(BaseModel):
    id: UUID
    name: str
    team_id: UUID | None
    status: Status
    created_at: datetime
    deadline: datetime

    class Config:
        from_attributes = True


class ProjectDetailSchema(BaseModel):
    id: UUID
    name: str
    description: str | None
    team_id: UUID | None
    status: Status
    created_by: UUID
    created_at: datetime
    deadline: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ProjectCreateSchema(BaseModel):
    name: str
    description: str | None
    team_id: UUID | None
    deadline: datetime


class ProjectUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    team_id: UUID | None = None
    status: Status | None = None
    deadline: datetime | None = None
    is_active: bool | None = None
