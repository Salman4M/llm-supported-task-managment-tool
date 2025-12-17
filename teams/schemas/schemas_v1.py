from uuid import UUID
from pydantic import BaseModel
from typing import List

class TeamCreate(BaseModel):
    name: str
    description: str | None = None
    member_ids: List[UUID] = []

class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    member_ids: List[UUID] | None = None
