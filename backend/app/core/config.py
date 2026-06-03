from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    project_name: str = 'Lanas Pau Pricing'
    api_v1_prefix: str = '/api/v1'
    secret_key: str = 'change-me'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 480
    database_url: str = 'postgresql+psycopg2://postgres:postgres@localhost:5432/revesderecho'
    backend_cors_origins: str = 'http://localhost:5173,https://lanaspau-frontend.onrender.com'
    default_admin_email: str = 'admin@lanaspau.cl'
    default_admin_password: str = 'LanasPau_Admin_9x$2024!'

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(',') if origin.strip()]

settings = Settings()
