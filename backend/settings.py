from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LARGE_GPT_MODEL = "gpt-4-turbo-preview"
SMALL_GPT_MODEL = "gpt-3.5-turbo"


class Settings(BaseSettings):
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    google_credentials: str | None = Field(default=None)
    gpt_model: str = Field(default=LARGE_GPT_MODEL)
    gpt_small_model: str = Field(default=SMALL_GPT_MODEL)
    redis_tls_url: RedisDsn | None = Field(default=None)
    redis_url: RedisDsn = Field(default="redis://localhost:6379/1")
    secret_key: str = Field(default="")
    system_openai_api_key: str | None = Field(default=None)
    encryption_key: bytes = Field(default=b"")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
