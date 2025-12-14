from sqlalchemy.orm import Session
from users.models.models_v1 import User
from fastapi import APIRouter, Depends,Body,Request
from fastapi.security import HTTPAuthorizationCredentials
from core.authentication import get_current_user,security
from core.database import get_db
from users.schemas.schemas_v1  import RegisterSchema, LoginSchema, TokenSchema,ChangePasswordSchema,UserSchema,RegisterResponseSchema,UserListSchema
from users.services.service_v1 import user_service
from json import JSONDecodeError
from typing import List

router = APIRouter(prefix="/api", tags=["Users"])

#for po
@router.post('/register',response_model = RegisterResponseSchema)
def register(user_in: RegisterSchema, db: Session = Depends(get_db)):
    return user_service.register_user(db,user_in)

#for member
@router.post('/create-member', response_model=UserSchema)
def create_team_member(
    user_in: RegisterSchema, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    return user_service.register_user(db, user_in, current_user=current_user)


@router.post('/login')
async def login(user_in: LoginSchema,db:Session = Depends(get_db)):
    return user_service.login_user(db, user_in)

@router.post("/refresh", response_model=TokenSchema)
async def refresh(
    refresh_token: str = Body(..., embed=True), 
    db: Session = Depends(get_db)
):
    return await user_service.refresh_token(db, refresh_token)

@router.post("/logout")
async def logout(
    request: Request,
    auth: HTTPAuthorizationCredentials = Depends(security) 
):
    token = auth.credentials
    # Try to get refresh token from body if sent
    refresh_token = None
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
    except JSONDecodeError:
        # If body is empty/invalid, just ignore it. 
        # We still want to log out the Access Token!
        pass
    
    return await user_service.logout_user(token, refresh_token)


@router.patch("/change-password")
async def change_password(
    password_in: ChangePasswordSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):

    return user_service.change_password(db, current_user.id, password_in)

@router.delete("/delete-user")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    return user_service.delete_user(db,current_user.id, user_id)


@router.get("/my-users",response_model=List[UserListSchema])
async def get_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.get_my_members(db,current_user.id)

@router.get("/my-pos",response_model = List[UserSchema])
async def get_pos(
    db:Session = Depends(get_db)
):
    return user_service.get_project_owners(db)