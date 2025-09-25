from app.repositories.user_repo import UserRepository
from app.repositories.team_repo import TeamRepository

class UserService:
    def __init__(self, user_repo: UserRepository, team_repo: TeamRepository):
        self.user_repo = user_repo
        self.team_repo = team_repo

    def create_user(self, name: str, team_id=None):
        if team_id:
            team = self.team_repo.get_team_by_id(team_id)
            if not team:
                raise ValueError(f"Team with id {team_id} does not exist")
        return self.user_repo.create_user(name, team_id)

    def get_user(self, user_id):
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        return user

    def list_users(self):
        return self.user_repo.get_all_users()

    def assign_to_team(self, user_id, team_id):
        user = self.get_user(user_id)
        team = self.team_repo.get_team_by_id(team_id)
        if not team:
            raise ValueError(f"Team with id {team_id} does not exist")
        user.team_id = team_id
        self.user_repo.db.commit()
        self.user_repo.db.refresh(user)
        return user
