from fastapi import Depends, HTTPException ,status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from core.security import is_token_blacklisted
from users.repositories.repository_v1 import user_repo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentical_exception = HTTPException(
        401,
        "Could not validate credenticals",
        headers = {"WWW-Authenticate":"Bearer"}
    )
    if await is_token_blacklisted(token):
        raise HTTPException(401,"Token has been revoked (logged out)")
    
    try:
        payload = jwt.decode(token,settings.JWT_SECRET,algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentical_exception
    except JWTError:
        raise credentical_exception
    
    user = user_repo.get_by_id(db, user_id=user_id)
    if user is None:
        raise credentical_exception
    
    return user

