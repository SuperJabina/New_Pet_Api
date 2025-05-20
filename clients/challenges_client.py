from clients.base_client import BaseClient
from config.api_routes import APIRoutes
import allure
from httpx import Response
from typing import Optional

class ChallengesClient(BaseClient):
    """
    Клиент для работы с эндпоинтом /challenges API_CHALLENGES.
    """
    def __init__(self, client):
        super().__init__(client)

    @allure.step("Get all challenges")
    def get_challenges_api(self, headers: Optional[dict[str, str]] = None, params: Optional[dict[str, str]] = None) -> Response:
        """
        Получает список всех заданий.

        Args:
            headers: Дополнительные заголовки для запроса (переопределяют дефолтные).
            params: Query-параметры для запроса.
        """
        return self.get(APIRoutes.CHALLENGES.value, headers=headers, params=params)