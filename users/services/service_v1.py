from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from users.models.models_v1 import User
from users.repositories.repository_v1 import user_repo
from users.schemas.schemas_v1 import RegisterSchema,LoginSchema,ChangePasswordSchema
from passlib.context import CryptContext
from jose import jwt,JWTError
from users.utils.enum import UserRole
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
    def register_user(self,db: Session, schema: RegisterSchema,current_user: Optional[User] = None):
        if user_repo.get_by_email(db, schema.email):
            raise HTTPException(
                400,
                "email already registered"
            )
        user_dict = schema.model_dump(exclude = {"confirm_password"})

        if current_user:
            current_user = user_repo.get_by_id(db,current_user.id)
            if current_user.role!='project_owner':
                raise HTTPException(
                    401,
                    "Only Project Owner can create new members"
                )
            user_dict['created_by'] = current_user.id
        else:
            pass
            
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
            payload = jwt.decode(refresh_token,settings.JWT_SECRET,algorithms=[settings.JWT_ALGORITHM])
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

    def change_password(self, db: Session,user_id: str, schema: ChangePasswordSchema):
        user = user_repo.get_by_id(db,user_id)

        if not user or not verify_password(schema.old_password,user.password):
            raise HTTPException(
                401,
                "Incorrect old password"
            )
        new_hash = get_password_hash(schema.new_password)
        user_repo.update_password(db,user_id,new_hash)
        
        return {"message":"password updated successfully"}
    

    def delete_user(self, db: Session, current_user_id :str, deleted_user_id: str):
        current_user = user_repo.get_by_id(db,current_user_id)
        deleted_user = user_repo.get_by_id(db,deleted_user_id)
        if current_user.role != 'project_owner' or deleted_user.created_by != current_user.id:
            raise HTTPException(
                401,
                "You are not allowed to delete user"
            )
        user_repo.delete(db,deleted_user_id)
        return {"message":"User deleted successfully"}

    def get_my_members(self, db: Session, current_user_id:str):
        return user_repo.get_users(db,current_user_id)

    def get_project_owners(self,db:Session):
        return user_repo.get_pos(db)

user_service = UserService()
