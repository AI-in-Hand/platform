from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LATEST_GPT_MODEL = "gpt-4-turbo-preview"
CHEAP_GPT_MODEL = "gpt-3.5-turbo-1106"


class Settings(BaseSettings):
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    airtable_token: str | None = Field(default=None)
    airtable_base_id: str | None = Field(default=None)
    airtable_table_id: str | None = Field(default=None)

    google_credentials: str | None = Field(default=None)
    gpt_model: str = Field(default=LATEST_GPT_MODEL)
    gpt_cheap_model: str = Field(default=CHEAP_GPT_MODEL)
    openai_api_key: str | None = Field(default=None)
    redis_tls_url: RedisDsn | None = Field(default=None)
    redis_url: RedisDsn = Field(default="redis://localhost:6379/1")
    secret_key: str | None = Field(default=None)

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
