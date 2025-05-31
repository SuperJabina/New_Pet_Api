import pytest
from config.settings import Settings
from tools.logger import get_logger
from pydantic import ValidationError

logger = get_logger(__name__)

@pytest.fixture(scope="session")
def settings() -> Settings:
    """
        Фикстура создаёт объект с настройками один раз на всю тестовую сессию.

        Возвращает объект класса Settings с конфигурацией для тестирования API.
        В случае ошибки валидации настроек логирует проблему и выбрасывает исключение.
        """
    # Попытка создания объекта настроек
    try:
        logger.info("Attempting to load settings for test session")
        settings = Settings()
        # Логирование успешно загруженных настроек
        logger.debug(f"Settings loaded successfully: {settings.model_dump()}")
        logger.info("Settings fixture initialized for test session")
        return settings
    # Обработка ошибок валидации настроек
    except ValidationError as e:
        logger.error(f"Failed to load settings: {e}")
        raise
