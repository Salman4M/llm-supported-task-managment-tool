from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import delete

from teams.models.models_v1 import Team, team_members
from users.models.models_v1 import User
from teams.schemas.schemas_v1 import TeamCreate, TeamUpdate


class TeamRepository:

    def get_all(self, db: Session):
        return db.query(Team).all()

    def get_by_id(self, db: Session, team_id: UUID):
        return db.query(Team).filter(Team.id == team_id).first()

    def create(self, db: Session, team: TeamCreate, creator_id: UUID):
        db_team = Team(
            name=team.name,
            description=team.description,
            created_by=creator_id
        )

        if team.member_ids:
            members = (
                db.query(User)
                .filter(User.id.in_(team.member_ids))
                .all()
            )
            db_team.team_members = members

        db.add(db_team)
        db.commit()
        db.refresh(db_team)
        return db_team

    def update(self, db: Session, team_id: UUID, team: TeamUpdate):
        db_team = self.get_by_id(db, team_id)
        if not db_team:
            return None

        if team.name is not None:
            db_team.name = team.name

        if team.description is not None:
            db_team.description = team.description

        if team.member_ids is not None:
            members = (
                db.query(User)
                .filter(User.id.in_(team.member_ids))
                .all()
            )
            db_team.team_members = members

        db.commit()
        db.refresh(db_team)
        return db_team

    def delete(self, db: Session, team_id: UUID):
        db_team = self.get_by_id(db, team_id)
        if not db_team:
            return None

        db.delete(db_team)
        db.commit()
        return True
    
    def add_member(self, db: Session, team_id: UUID, user_id: UUID):
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(404, "Team not found")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(404, "User not found")

        if user in team.team_members:
            raise HTTPException(400, "User already in team")

        team.team_members.append(user)
        db.commit()
        db.refresh(team)
        return team
    
    def get_members(self, db: Session, team_id):
        team = db.query(Team).filter(Team.id == team_id).first()

        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return team.team_members

    def get_user(self, db: Session, user_id: UUID):
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_id(self, db: Session, team_id: UUID) -> Team | None:
        return db.query(Team).filter(Team.id == team_id).first()

    def remove_member(self, db: Session, team_id: UUID, user_id: UUID):
        member = (
            db.query(team_members)
            .filter(
                team_members.c.team_id == team_id,
                team_members.c.user_id == user_id
            )
            .first()
        )

        if not member:
            return None  # və ya HTTPException 404

        db.execute(
            team_members.delete().where(
                team_members.c.team_id == team_id,
                team_members.c.user_id == user_id
            )
        )
        db.commit()

