from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.team_repo import TeamRepository

router = APIRouter(prefix="/teams")

@router.post("/")
def create_team(team_data: dict, db: Session = Depends(get_db)):
    """Create a new team (Admin only)"""
    team_repo = TeamRepository(db)
    
    name = team_data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    return team_repo.create_team(name)

@router.get("/{team_id}")
def get_team(team_id: str, db: Session = Depends(get_db)):
    """Get a specific team by ID (Admin only)"""
    team_repo = TeamRepository(db)
    team = team_repo.get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.get("/")
def list_teams(db: Session = Depends(get_db)):
    """List all teams (Admin only)"""
    team_repo = TeamRepository(db)
    return team_repo.get_all_teams()

@router.put("/{team_id}")
def update_team(team_id: str, update_data: dict, db: Session = Depends(get_db)):
    """Update team details (Admin only)"""
    team_repo = TeamRepository(db)
    team = team_repo.update_team(team_id, update_data)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.delete("/{team_id}")
def delete_team(team_id: str, db: Session = Depends(get_db)):
    """Delete a team (Admin only)"""
    team_repo = TeamRepository(db)
    team = team_repo.delete_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": f"Team {team_id} deleted successfully"}

@router.get("/{team_id}/users")
def get_team_users(team_id: str, db: Session = Depends(get_db)):
    """Get all users in a team (Admin only)"""
    from app.repositories.user_repo import UserRepository
    
    team_repo = TeamRepository(db)
    user_repo = UserRepository(db)
    
    team = team_repo.get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    users = user_repo.get_users_by_team(team_id)
    return {
        "team": team,
        "users": users,
        "user_count": len(users)
    }