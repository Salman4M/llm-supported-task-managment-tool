from sqlalchemy.orm import Session
from users.models.models_v1 import User


class UserRepository:
    def get_by_email(self, db: Session, email:str):
        return db.query(User).filter(User.email==email).first()
    
    def get_by_id(self, db: Session, user_id: str):
        return db.query(User).filter(User.id == user_id).first()
    
    def get_users(self,db: Session):
        return db.query(User).filter(User.role!='product_owner').all()

    def create(self, db: Session,user_data: dict):
        new_user = User(**user_data)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    def delete(self, db:Session, user_id: str):
        return db.query(User).filter(User.id==user_id).delete()

    def update_password(self,db:Session,user_id: str, hashed_password: str):
        user = self.get_by_id(db,user_id)
        if user:
            user.password = hashed_password
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

user_repo = UserRepository()



