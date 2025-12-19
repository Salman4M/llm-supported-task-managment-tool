from uuid import uuid4

from projects.utils.enum import Status

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Table,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


team_members = Table(
    "team_members",
    Base.metadata,
    Column("team_id", PGUUID(as_uuid=True), ForeignKey("teams.id"), primary_key=True),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
)


class Team(Base):
    __tablename__ = "teams"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    projects = relationship("Project", back_populates="team")
    creator = relationship("User", foreign_keys=[created_by])
    team_members = relationship("User", secondary=team_members, backref="teams")