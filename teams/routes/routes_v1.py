from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi import Query

from core.database import get_db
from core.authentication import get_current_user
from users.models.models_v1 import User
from teams.schemas.schemas_v1 import TeamCreate, TeamUpdate
from teams.services.services_v1 import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])
service = TeamService()

#CRUD
@router.get("/")
def get_teams(db: Session = Depends(get_db)):
    return service.get_all(db)

@router.get("/{team_id}")
def get_team(team_id: UUID, db: Session = Depends(get_db)):
    return service.get_by_id(db, team_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create(db, team, current_user)

@router.put("/{team_id}")
def update_team(
    team_id: UUID,
    team: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.update(db, team_id, team, current_user)

@router.delete("/{team_id}")
def delete_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.delete(db, team_id, current_user)


#Other
@router.post("/{team_id}/members")
def add_team_member(
    team_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Add a user to a team.
    Only the team lead can add members.
    """
    return service.add_member(
        db=db,
        team_id=team_id,
        user_id=user_id,
        current_user=current_user
    )

@router.get("/{team_id}/members")
def get_team_members(
    team_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service.get_members(
        db=db,
        current_user=current_user,
        team_id=team_id,
    )

@router.delete("/{team_id}/members/{user_id}")
def delete_team_member(
    team_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service.delete_member(
        db=db,
        current_user=current_user,
        team_id=team_id,
        user_id=user_id,
    )
