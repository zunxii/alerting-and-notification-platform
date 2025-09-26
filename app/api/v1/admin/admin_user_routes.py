from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.repositories.team_repo import TeamRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users")

@router.post("/")
def create_user(user_data: dict, db: Session = Depends(get_db)):
    """Create a new user (Admin only)"""
    user_repo = UserRepository(db)
    team_repo = TeamRepository(db)
    user_service = UserService(user_repo, team_repo)
    
    name = user_data.get("name")
    team_id = user_data.get("team_id")
    
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    return user_service.create_user(name, team_id)

@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get a specific user by ID (Admin only)"""
    user_repo = UserRepository(db)
    team_repo = TeamRepository(db)
    user_service = UserService(user_repo, team_repo)
    
    try:
        return user_service.get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    """List all users (Admin only)"""
    user_repo = UserRepository(db)
    team_repo = TeamRepository(db)
    user_service = UserService(user_repo, team_repo)
    return user_service.list_users()

@router.put("/{user_id}")
def update_user(user_id: str, update_data: dict, db: Session = Depends(get_db)):
    """Update user details (Admin only)"""
    user_repo = UserRepository(db)
    user = user_repo.update_user(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}/team")
def assign_user_to_team(user_id: str, team_data: dict, db: Session = Depends(get_db)):
    """Assign user to a team (Admin only)"""
    user_repo = UserRepository(db)
    team_repo = TeamRepository(db)
    user_service = UserService(user_repo, team_repo)
    
    team_id = team_data.get("team_id")
    if not team_id:
        raise HTTPException(status_code=400, detail="team_id is required")
    
    try:
        return user_service.assign_to_team(user_id, team_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete a user (Admin only)"""
    user_repo = UserRepository(db)
    user = user_repo.delete_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} deleted successfully"}