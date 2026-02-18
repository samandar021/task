from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "observability-demo"
    app_env: str = "dev"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/appdb"
    log_level: str = "INFO"
    log_file: str = "/app/logs/app.log"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
