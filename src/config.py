from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_name: str
    api_version: str
    api_summary: str
    developer_email: str
    developer_name: str
    developer_profile: str

    model_config= SettingsConfigDict(env_file=".env")

settings = Settings()