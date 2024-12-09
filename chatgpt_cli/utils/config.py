from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """
    Configuration settings for the database connection.
    Reads environment variables with the prefix 'DB_'.
    """

    user: str = Field(..., description="Database username.")
    password: SecretStr = Field(..., description="Database password.")
    host: str = Field(..., description="Database host address.")
    port: int = Field(..., description="Database port number.")
    name: str = Field(..., description="Database name.")
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    pool_pre_ping: bool = True

    class Config:
        env_prefix = "DB_"
        validate_assignment = True

    @property
    def url(self) -> str:
        """
        Constructs the full database URL.
        """
        password = self.password.get_secret_value()
        return f"postgresql+asyncpg://{self.user}:{password}@{self.host}:{self.port}/{self.name}"

    @field_validator("port")
    def validate_port(cls, value):
        """
        Validates that the port number is within the valid range.
        """
        if not (1 <= value <= 65535):
            raise ValueError("Port must be between 1 and 65535.")
        return value


class OpenAISettings(BaseSettings):
    """
    Configuration settings for the OpenAI API.
    Reads environment variables with the prefix 'OPENAI_'.
    """

    api_key: SecretStr = Field(..., description="OpenAI API key.")

    class Config:
        env_prefix = "OPENAI_"
        validate_assignment = True

    @field_validator("api_key")
    def validate_api_key(cls, value):
        """
        Validates that the API key starts with the expected prefix.
        """
        key = value.get_secret_value()
        if not key.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format.")
        return value


class Settings(BaseSettings):
    """
    Main application settings encompassing all configuration sections.
    """

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)

    class Config:
        env_nested_delimiter = "__"


settings = Settings()
