from sqlalchemy.orm import Session
from app.models.team import Team

class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_team(self, name: str) -> Team:
        team = Team(name=name)
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)
        return team

    def get_team_by_id(self, team_id: str):
        return self.db.query(Team).filter(Team.id == team_id).first()

    def get_all_teams(self):
        return self.db.query(Team).all()

    def update_team(self, team_id: str, update_data: dict):
        team = self.get_team_by_id(team_id)
        if team:
            for key, value in update_data.items():
                if hasattr(team, key):
                    setattr(team, key, value)
            self.db.commit()
            self.db.refresh(team)
        return team

    def delete_team(self, team_id: str):
        team = self.get_team_by_id(team_id)
        if team:
            self.db.delete(team)
            self.db.commit()
        return team
