"""Configuration management for the QByte GL Data Service."""
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    app_name: str = Field(default="QByte GL Data Service", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # Database Configuration
    database_url: str | None = Field(default=None, env="DATABASE_URL")

    # Redis Configuration
    redis_url: str | None = Field(default=None, env="REDIS_URL")

    # Data Generation Configuration
    historical_days: int = Field(default=365, env="HISTORICAL_DAYS")
    streaming_interval_seconds: float = Field(default=30.0, env="STREAMING_INTERVAL_SECONDS")
    fixed_start_date: str = Field(default="2025-11-10", env="FIXED_START_DATE")
    random_seed: int = Field(default=42, env="RANDOM_SEED")

    # External APIs
    eia_api_key: str | None = Field(default=None, env="EIA_API_KEY")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
