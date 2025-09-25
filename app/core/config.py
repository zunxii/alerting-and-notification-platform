from pydantic_settings import BaseSettings

class Config(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = Config()
