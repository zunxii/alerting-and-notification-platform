from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, name: str, team_id: str = None) -> User:
        user = User(name=name, team_id=team_id)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: str):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user(self, user_id: str):
        return self.get_user_by_id(user_id)

    def get_all_users(self):
        return self.db.query(User).all()

    def get_users_by_team(self, team_id: str):
        return self.db.query(User).filter(User.team_id == team_id).all()

    def update_user(self, user_id: str, update_data: dict):
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, user_id: str):
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
        return user
