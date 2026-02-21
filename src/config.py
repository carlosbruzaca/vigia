from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str | None = None
    telegram_bot_token: str
    environment: str = "development"
    log_level: str = "INFO"


settings = Settings()
