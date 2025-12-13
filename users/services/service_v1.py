from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from users.repositories.repository_v1 import user_repo
from users.schemas.schemas_v1 import RegisterSchema,LoginSchema
from passlib.context import CryptContext
from jose import jwt,JWTError
from core.config import settings


from core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    add_to_blacklist,
    is_token_blacklisted
)

pwd_content = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def register_user(self,db: Session, schema: RegisterSchema):
        if user_repo.get_by_email(db, schema.email):
            raise HTTPException(
                400,
                "email already registered"
            )
        
        user_dict = schema.model_dump(exclude = {"confirm_password"})
        user_dict["password"] = get_password_hash(user_dict["password"])

        return user_repo.create(db, user_dict)

    def login_user(self, db: Session, schema: LoginSchema):
        user = user_repo.get_by_email(db,schema.email)
        if not user or not pwd_content.verify(schema.password, user.password):
            raise HTTPException(
                401,
                "incorrect email or password",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer"
        }
    
    async def logout_user(self,access_token: str, refresh_token: str = None):
        await add_to_blacklist(access_token)

        if refresh_token:
            await add_to_blacklist(refresh_token)
        
        return {"message":"Successfully logged out"}
    
    async def refresh_token(self, db:Session, refresh_token: str):
        if await is_token_blacklisted(refresh_token):
            raise HTTPException(401,"refresh token revoked")
        
        try:
            payload = jwt.decode(refresh_token,settings.SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
            if not user_id or payload.get("type") != "refresh":
                raise HTTPException(401,"Invalid token type")
            
            await add_to_blacklist(refresh_token)

            return {
                "access_token": create_access_token(user_id),
                "refresh_token": create_refresh_token(user_id),
                "token_type": "bearer"
            }
        except JWTError:
            raise HTTPException(401,"Invalid refresh token")

        

user_service = UserService()
