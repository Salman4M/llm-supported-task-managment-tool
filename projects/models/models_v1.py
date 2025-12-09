from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from projects.utils import ProjectStatus

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy import Column, DateTime, String, Enum,Table as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from users.utils import UserRole
Base = declarative_base()



team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', PGUUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True),
    Column('user_id', PGUUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
)

class Project(Base):
    __tablename__ = "projects"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    team_id = Column(PGUUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)    
    status = Column(SQLEnum(ProcessLookupError),nullable=False, default=ProcessLookupError.to_do)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    creator = relationship("User", back_populates="projects")
    teams = relationship("Team", back_populates="project")




class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.todo)
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    parent = relationship("Task", remote_side=[id], backref="subtasks")
    assigned_user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")



# SQLAlchemy Model
class Team(Base):
    __tablename__ = "teams"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="teams")
    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("User", secondary=team_members, backref="teams")