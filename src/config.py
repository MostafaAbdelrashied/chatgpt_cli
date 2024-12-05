import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY")
    DATABASE_URL: str = os.environ.get("DATABASE_URL")


settings = Settings()
