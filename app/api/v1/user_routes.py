from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.repositories.team_repo import TeamRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
def create_user(name: str, team_id: str = None, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    team_repo = TeamRepository(db)
    user_service = UserService(user_repo, team_repo)
    return user_service.create_user(name, team_id)

@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    team_repo = TeamRepository(db)
    user_service = UserService(user_repo, team_repo)
    return user_service.get_user(user_id)

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    team_repo = TeamRepository(db)
    user_service = UserService(user_repo, team_repo)
    return user_service.list_users()
