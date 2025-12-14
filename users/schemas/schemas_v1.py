#schemas
from users.utils.enum import UserRole
from pydantic import BaseModel,Field,EmailStr, model_validator
from typing import Optional
from datetime import datetime
import uuid

class RegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str = Field(nullable = False)
    role: UserRole = UserRole.project_owner
    created_by: Optional[uuid.UUID] = None
    specialty: str
    created_at: Optional[datetime] = None
    
    @model_validator(mode='after')
    def check_password_match(self) -> 'RegisterSchema':
        if self.password != self.confirm_password:
            raise ValueError("Passwords don't match")
        return self


class LoginSchema(BaseModel):
    email: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


    @model_validator(mode='after')
    def check_password(self) -> 'ChangePasswordSchema':
        if self.new_password != self.confirm_password:
            raise ValueError("New passwords don't match")
        return self
    
