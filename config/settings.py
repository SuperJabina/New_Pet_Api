from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from tools.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    """
    Настройки проекта для тестирования API.

    Загружает переменные из файлов `.env`, `.env.test`, `.env.prod`.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Игнорировать лишние переменные
    )

    api_url: HttpUrl
    api_timeout: float = 10.0
    api_x_challenger: str
    log_level: str = "DEBUG"  # Уровень логирования по умолчанию

    @field_validator("api_timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

    @field_validator("api_x_challenger")
    @classmethod
    def validate_x_challenger(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("X-Challenger token cannot be empty")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug(f"Settings: {self.model_dump()}")