from uuid import uuid4

from projects.utils.enum import Status

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    team_id = Column(PGUUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    status = Column(SQLEnum(Status), nullable=False, default=Status.to_do)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    deadline = Column(DateTime(timezone=True), nullable=False)
    is_active = Column((Boolean), default=True)

    creator = relationship("User", back_populates="projects")
    team = relationship("Team", back_populates="projects")
    tasks = relationship("Task", back_populates="project")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    status = Column(SQLEnum(Status), nullable=False, default=Status.to_do)
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parent = relationship("Task", remote_side=[id], backref="subtasks")
    assigned_user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")


# class Team(Base):
#     __tablename__ = "teams"

#     id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     created_at = Column(
#         DateTime(timezone=True), server_default=func.now(), nullable=False
#     )

#     projects = relationship("Project", back_populates="team")
#     creator = relationship("User", foreign_keys=[created_by])
#     members = relationship("User", secondary=team_members, backref="teams")
