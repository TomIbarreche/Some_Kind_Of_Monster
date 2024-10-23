from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mail_username: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    mail_starttls: bool
    mail_ssl_tls: bool
    use_credentials: bool
    validate_certs: bool
    default_admin_email: str

    model_config= SettingsConfigDict(env_file=".env")

settings = Settings()
