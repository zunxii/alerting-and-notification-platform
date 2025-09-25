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

    def get_team_by_id(self, team_id):
        return self.db.query(Team).filter(Team.id == team_id).first()

    def get_all_teams(self):
        return self.db.query(Team).all()
