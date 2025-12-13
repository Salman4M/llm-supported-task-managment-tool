from schemas.schemas_v1 import RegisterSchema, LoginSchema
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,Body,Request
from core.config import settings
from core.authentication import oauth2_scheme
from core.database import get_db
from core.security import create_access_token, create_refresh_token
from users.schemas.schemas_v1  import RegisterSchema, LoginSchema, TokenSchema
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
    token: str = Depends(oauth2_scheme) # Gets the Access Token
):
    # Try to get refresh token from body if sent
    body = await request.json()
    refresh_token = body.get("refresh_token")
    
    return await user_service.logout_user(token, refresh_token)