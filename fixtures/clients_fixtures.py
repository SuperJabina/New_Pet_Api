import pytest
import httpx
from config.settings import Settings
from clients.challenges_client import ChallengesClient
from clients.todos_client import TodosClient
from tools.logger import get_logger
from pydantic import ValidationError
from typing import Iterator

logger = get_logger(__name__)

@pytest.fixture(scope="session")
def client(settings: Settings) -> Iterator[httpx.Client]:
    """
    Фикстура создаёт HTTP-клиент с настройками из Settings.
    """
    client = httpx.Client(
        base_url=str(settings.api_url),
        timeout=settings.api_timeout,
        headers={"X-Challenger": settings.api_x_challenger}
    )
    yield client
    logger.debug("Closing HTTP client")
    client.close()

@pytest.fixture(scope="session")
def challenges_client(client: httpx.Client) -> ChallengesClient:
    """
    Фикстура создаёт ChallengesClient.
    """
    return ChallengesClient(client=client)

@pytest.fixture(scope="session")
def todos_client(client: httpx.Client) -> TodosClient:
    """
    Фикстура создаёт ChallengesClient.
    """
    return TodosClient(client=client)