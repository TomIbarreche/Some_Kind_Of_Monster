from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_name: str
    api_version: str
    api_summary: str
    api_prefix: str
    developer_email: str
    developer_name: str
    developer_profile: str
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    default_admin_username: str
    default_admin_email: str
    default_admin_password: str
    access_token_expire_minutes: int

    model_config= SettingsConfigDict(env_file=".env")

settings = Settings()