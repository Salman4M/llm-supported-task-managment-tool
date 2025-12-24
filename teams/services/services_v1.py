from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from users.utils.enum import UserRole
from teams.repositories.repository_v1 import TeamRepository
from teams.schemas.schemas_v1 import TeamCreate, TeamUpdate
from users.models.models_v1 import User


class TeamService:
    def __init__(self):
        self.repo = TeamRepository()

    #CRUD
    def get_all(self, db: Session):
        return self.repo.get_all(db)

    def get_by_id(self, db: Session, team_id: UUID):
        team = self.repo.get_by_id(db, team_id)
        if not team:
            raise HTTPException(404, "Team not found")
        return team

    def create(self, db: Session, team: TeamCreate, user: User):
        if user.role != UserRole.project_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Project Owner can create team"
            )
        return self.repo.create(
            db=db,
            team=team,
            creator_id=user.id
        )

    def update(
        self,
        db: Session,
        team_id: UUID,
        team: TeamUpdate,
        user: User
    ):
        db_team = self.repo.get_by_id(db, team_id)
        if not db_team:
            raise HTTPException(404, "Team not found")

        if db_team.created_by != user.id:
            raise HTTPException(403, "Not allowed")

        return self.repo.update(db, team_id, team)

    def delete(self, db: Session, team_id: UUID, user: User):
        db_team = self.repo.get_by_id(db, team_id)
        if not db_team:
            raise HTTPException(404, "Team not found")

        if db_team.created_by != user.id:
            raise HTTPException(403, "Not allowed")

        self.repo.delete(db, team_id)
        return {"message": "Team deleted"}
    
    #Other
    def add_member(self, db: Session, team_id: UUID, user_id: UUID, current_user):
        team = self.repo.get_by_id(db, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # ✅ Fixed: Logic error - should be OR not AND
        if current_user.role not in [UserRole.project_owner, UserRole.team_lead]:
            raise HTTPException(
                status_code=403, 
                detail="Only team lead and project owner can add members"
            )

        user = self.repo.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user is already a member using get_members
        members = self.get_members(db, current_user, team_id)
        if any(member.id == user_id for member in members):
            raise HTTPException(
                status_code=400, 
                detail="User is already a member of the team"
            )

        return self.repo.add_member(db, team_id, user_id)

    def get_members(self, db, current_user, team_id):
        team = self.repo.get_members(db, team_id)
        return team
    
    def delete_member(self, db: Session, current_user: User, team_id: UUID, user_id: UUID):
        team = self.repo.get_by_id(db, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        members = self.repo.get_members(db, team_id)
        member_ids = [member.id for member in members]

        # Check if user is a member
        if user_id not in member_ids:
            raise HTTPException(
                status_code=404, 
                detail="User is not a member of the team"
            )

        # Authorization
        if current_user.role == UserRole.project_owner:
            # PO can delete anyone
            self.repo.remove_member(db, team_id, user_id)
        elif current_user.role == UserRole.team_lead:
            # Team Lead can delete only members (not PO, not other team leads)
            user_to_delete = next((m for m in members if m.id == user_id), None)
            if not user_to_delete:
                raise HTTPException(status_code=404, detail="User not found in team")
            if user_to_delete.role in [UserRole.project_owner, UserRole.team_lead]:
                raise HTTPException(
                    status_code=403, 
                    detail="Team Lead cannot remove this user"
                )
            self.repo.remove_member(db, team_id, user_id)
        else:
            raise HTTPException(
                status_code=403, 
                detail="Not allowed to remove members"
            )

        return {"detail": "Member removed successfully"}