import pytest
import httpx
from config.settings import Settings
from clients.challenges_client import ChallengesClient
from clients.todos_client import TodosClient
from tools.logger import get_logger
from typing import Iterator

logger = get_logger(__name__)

@pytest.fixture(scope="session")
def client(settings: Settings) -> Iterator[httpx.Client]:
    """
    Фикстура создаёт HTTP-клиент с настройками из Settings.

    :param settings: Объект настроек из класса Settings
    :return: Итератор, предоставляющий HTTP-клиент httpx.Client
    """
    logger.info("Creating HTTP client for test session")
    try:
        client = httpx.Client(
            base_url=str(settings.api_url),
            timeout=settings.api_timeout
        )
        logger.debug(f"HTTP client created with base URL: {settings.api_url} and timeout: {settings.api_timeout}")
        yield client
        # Логирование закрытия клиента
        logger.debug("Closing HTTP client")
        client.close()
        logger.info("HTTP client closed successfully")
    except Exception as e:
        # Логирование ошибки при создании или закрытии клиента
        logger.error(f"Failed to create or close HTTP client: {e}")
        raise

@pytest.fixture(scope="session")
def challenges_client(client: httpx.Client) -> ChallengesClient:
    """
    Фикстура создаёт ChallengesClient.

    :param client: HTTP-клиент httpx.Client
    :return: Экземпляр ChallengesClient для работы с API вызовов
    """
    logger.info("Creating ChallengesClient for test session")
    try:
        challenges_client = ChallengesClient(client=client)
        logger.debug("ChallengesClient initialized successfully")
        return challenges_client
    except Exception as e:
        # Логирование ошибки при создании ChallengesClient
        logger.error(f"Failed to create ChallengesClient: {e}")
        raise

@pytest.fixture(scope="session")
def todos_client(client: httpx.Client) -> TodosClient:
    """
    Фикстура создаёт TodosClient.

    :param client: HTTP-клиент httpx.Client
    :return: Экземпляр TodosClient для работы с API задач
    """
    logger.info("Creating TodosClient for test session")
    try:
        todos_client = TodosClient(client=client)
        logger.debug("TodosClient initialized successfully")
        return todos_client
    except Exception as e:
        # Логирование ошибки при создании TodosClient
        logger.error(f"Failed to create TodosClient: {e}")
        raise