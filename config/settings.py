from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from tools.logger import get_logger

# Инициализация логгера для текущего модуля
logger = get_logger(__name__)

# Загрузка переменных окружения из файлов .env
load_dotenv()
logger.info("Environment variables successfully loaded from .env file")

class Settings(BaseSettings):
    """
        Настройки проекта для тестирования API.

        Загружает переменные из файла `.env`.
        Предоставляет конфигурацию для URL API, таймаута, токена X-Challenger и уровня логирования.
        """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Логирование инициализированных настроек для отладки
        logger.debug(f"Settings initialized: {self.model_dump()}")
        logger.info("Settings class successfully instantiated")

    # Конфигурация для настроек Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        # env_file_encoding="utf-8", # Раскомментировать для указания кодировки файла, если необходимо
        extra="ignore"  # Игнорировать лишние переменные
    )

    api_url: HttpUrl
    api_timeout: float = 10.0
    api_x_challenger: str
    log_level: str = "DEBUG"  # Уровень логирования по умолчанию

    @field_validator("api_timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        # Валидация значения таймаута
        if v <= 0:
            logger.error("Invalid timeout value: must be positive")
            raise ValueError("Timeout must be positive")
        logger.debug(f"Timeout value {v} validated successfully")
        return v

    @field_validator("api_x_challenger")
    @classmethod
    def validate_x_challenger(cls, v: str) -> str:
        # Валидация токена X-Challenger
        if not v.strip():
            logger.error("Invalid X-Challenger token: cannot be empty")
            raise ValueError("X-Challenger token cannot be empty")
        logger.debug(f"X-Challenger token validated successfully")
        return v
