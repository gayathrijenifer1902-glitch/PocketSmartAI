from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    secret_key: str = "development-only-change-me"
    database_url: str = "sqlite:///./pocketsmart.db"
    access_token_expire_minutes: int = 480

settings = Settings()
