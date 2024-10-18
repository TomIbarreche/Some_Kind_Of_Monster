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
    mail_username: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    mail_starttls: bool
    mail_ssl_tls: bool
    use_credentials: bool
    validate_certs: bool
    verified_mail_subject: str
    domain_name: str
    url_secret_key: str
    url_email_salt: str
    password_reset_request_mail_subject: str

    model_config= SettingsConfigDict(env_file=".env")

settings = Settings()