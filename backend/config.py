"""Configuración centralizada: toda la app se controla desde variables de entorno (.env)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # Auth del dashboard y la API
    admin_user: str = Field(default="admin")
    admin_pass: str = Field(default="change_me")
    jwt_secret: str = Field(default="dev-secret-change-me")
    jwt_ttl_hours: int = Field(default=24)
    cookie_secure: bool = Field(default=False)

    # PostgreSQL
    database_url: str = Field(
        default="postgresql+asyncpg://portfolio:password@postgres:5432/portfolio"
    )

    # Imágenes subidas (volumen compartido con nginx)
    upload_dir: str = Field(default="/srv/uploads")

    # Dominio público permitido para Origin/Referer en /api/contact
    site_domain: str = Field(default="portfolio.julixr.com")

    # Evolution API — notificación de leads por WhatsApp
    evo_api_url: str = Field(default="")
    evo_instance: str = Field(default="")
    evo_api_key: str = Field(default="")
    evo_notify_number: str = Field(default="")


@lru_cache
def get_settings() -> Settings:
    return Settings()
