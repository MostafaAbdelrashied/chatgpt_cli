import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    DB_USER: str = os.environ["DB_USER"]
    DB_PASSWORD: SecretStr = os.environ["DB_PASSWORD"]
    DB_HOST: str = os.environ["DB_HOST"]
    DB_PORT: str = os.environ["DB_PORT"]
    DB_NAME: str = os.environ["DB_NAME"]

    @property
    def get_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:"
            f"{self.DB_PASSWORD.get_secret_value()}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )
