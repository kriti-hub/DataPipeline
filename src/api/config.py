"""API configuration module.

Loads all settings from environment variables with sensible defaults.
Uses Pydantic Settings for validation and type coercion.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    hris_api_key: str = "dev-api-key-change-me"
    hris_api_port: int = 8000
    api_title: str = "WellNow HRIS Simulated API"
    api_version: str = "1.0.0"
    api_description: str = (
        "Simulated HRIS REST API for WellNow Urgent Care staffing analytics."
    )

    # Data generation
    master_seed: int = 42
    num_locations: int = 80
    num_employees: int = 1200
    history_months: int = 18

    # CORS
    cors_origins: list[str] = ["*"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
