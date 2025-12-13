from sqlalchemy.orm import Session
from users.models.models_v1 import User


class UserRepository:
    def get_by_email(self, db: Session, email:str):
        return db.query(User).filter(User.email==email).first()
    
    def create(self, db: Session,user_data: dict):
        new_user = User(**user_data)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    

user_repo = UserRepository()



