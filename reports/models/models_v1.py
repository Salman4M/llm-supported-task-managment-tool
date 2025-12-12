from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from projects.utils.enum import Status

from sqlalchemy import Column, DateTime, String, ARRAY,Boolean,Float, Text, Integer, Table, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base



class UserReport(Base):
    __tablename__ = "user_reports"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    text = Column(Text, nullable=False)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_id = Column(ARRAY(Integer), nullable=True)  # List of task IDs
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_reports")


# SQLAlchemy Model
class LLMReport(Base):
    __tablename__ = "llm_reports"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    text = Column(Text, nullable=False)
    percentage = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
