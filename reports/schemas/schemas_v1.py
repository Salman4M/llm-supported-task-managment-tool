from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel


class UserReportCreate(BaseModel):
    text: str
    task_id: Optional[List[int]] = None


class UserReportUpdate(BaseModel):
    text: str
    task_id: Optional[List[int]] = None


class UserReportOut(BaseModel):
    id: UUID
    text: str
    user_id: UUID
    task_id: Optional[List[int]]
    is_verified: bool

    class Config:
        from_attributes = True


class LLMReportOut(BaseModel):
    id: UUID
    text: str
    percentage: float

    class Config:
        from_attributes = True
