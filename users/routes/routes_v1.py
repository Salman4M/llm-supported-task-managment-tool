from sqlalchemy.orm import Session
from models.models_v1 import User
from fastapi import APIRouter, Depends,Body,Request
from core.config import settings
from core.authentication import oauth2_scheme,get_current_user
from core.database import get_db
from users.schemas.schemas_v1  import RegisterSchema, LoginSchema, TokenSchema,ChangePasswordSchema
from users.services.service_v1 import user_service


router = APIRouter(prefix="/api", tags=["Users"])

@router.post('/register')
def register(user_in: RegisterSchema, db: Session = Depends(get_db)):
    return user_service.register_user(db,user_in)


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
    token: str = Depends(oauth2_scheme) 
):
    # Try to get refresh token from body if sent
    body = await request.json()
    refresh_token = body.get("refresh_token")
    
    return await user_service.logout_user(token, refresh_token)


@router.patch("/change/password")
async def change_password(
    password_in: ChangePasswordSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user())
    ):

    return user_service.change_password(db, current_user.id, password_in)

@router.delete("/delete/user")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user())
    ):
    return user_service.delete_user(db,current_user.id, user_id)
    