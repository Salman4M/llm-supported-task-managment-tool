from uuid import uuid4
from core.database import Base

from sqlalchemy import Column, DateTime, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from users.utils.enum import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Store hashed password
    role = Column(SQLEnum(UserRole), nullable=True, default=UserRole.project_owner)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    specialty = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    projects = relationship("Project", back_populates="creator")
    tasks = relationship("Task", back_populates="assigned_user")
    parent = relationship("User", remote_side=[id], backref="members")
    user_reports = relationship("UserReport", back_populates="user")




