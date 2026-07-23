from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_user: str
    postgres_password: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str

    jwt_secret: str
    jwt_expire_minutes: int = 60
    webhook_secret: str
    host: str = "0.0.0.0"
    port: int = 8000

    # Optional full URL (env: DATABASE_URL) — used by tests and rare overrides.
    database_url_override: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "database_url_override"),
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override

        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        auth = f"{user}:{password}@" if self.postgres_password else f"{user}@"
        return (
            f"postgresql+psycopg://{auth}"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    # Values come from env / .env via pydantic-settings, not constructor kwargs.
    return Settings()  # pyright: ignore[reportCallIssue]


settings = get_settings()
