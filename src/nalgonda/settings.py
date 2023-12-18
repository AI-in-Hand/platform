from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LATEST_GPT_MODEL = "gpt-4-1106-preview"


class Settings(BaseSettings):
    # openai_api_key: str = Field(validation_alias="OPENAI_API_KEY")
    gpt_model: str = Field(default=LATEST_GPT_MODEL, validation_alias="GPT_MODEL")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="AINHAND_", case_sensitive=True)


settings = Settings()
