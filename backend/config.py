from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    HERE_API_KEY made optional so tests can run without external secret.
    """

    HERE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None  # Alternative LLM provider
    EMBED_MODEL: str = "all-MiniLM-L6-v2"
    PORT: int = 8000
    # Caching and timeouts
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE: int = 1000
    HERE_HTTP_TIMEOUT_S: float = 5.0
    HERE_HTTP_RETRIES: int = 2
    ADDON_TIMEOUT_S: float = 3.0

    # Use absolute path to .env for reliability when cwd changes
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Export a singleton instance
settings = Settings()
