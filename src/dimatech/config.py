from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://redcoon@localhost:5432/dimatech"
    jwt_secret: str = "change-me-to-a-long-random-secret"
    jwt_expire_minutes: int = 60
    webhook_secret: str = "gfdmhghif38yrf9ew0jkf32"
    host: str = "0.0.0.0"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
