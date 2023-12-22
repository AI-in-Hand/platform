from pydantic import AliasChoices, Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LATEST_GPT_MODEL = "gpt-4-1106-preview"


class Settings(BaseSettings):
    openai_api_key: str | None = Field(default=None)
    gpt_model: str = Field(default=LATEST_GPT_MODEL)
    google_credentials: str | None = Field(default=None)
    redis_dsn: RedisDsn = Field(
        "redis://localhost:6379/1",
        validation_alias=AliasChoices("service_redis_dsn", "redis_url"),
    )

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
