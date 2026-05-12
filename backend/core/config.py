from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    railway_environment_name: str | None = None
    database_url: str = "sqlite:///./conversationiq.db"
    redis_url: str = "redis://localhost:6379"
    openai_api_key: str | None = None
    embedding_mode: str = "mock"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def normalized_openai_api_key(self) -> str | None:
        if self.openai_api_key is None:
            return None
        key = self.openai_api_key.strip()
        return key or None

    @property
    def is_production(self) -> bool:
        app_env = self.app_env.strip().lower()
        railway_env = (self.railway_environment_name or "").strip().lower()
        return app_env in {"production", "prod"} or railway_env in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
