import pytest
from config.settings import Settings
from tools.logger import get_logger
from pydantic import ValidationError

logger = get_logger(__name__)

@pytest.fixture(scope="session")
def settings() -> Settings:
    """
    Фикстура создаёт объект с настройками один раз на всю тестовую сессию.
    """
    try:
        settings = Settings()
        logger.debug(f"Loaded settings: {settings.model_dump()}")
        return settings
    except ValidationError as e:
        logger.error(f"Failed to load settings: {e}")
        raise
