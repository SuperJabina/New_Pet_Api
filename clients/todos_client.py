import os
from tools.logger import get_logger
from dotenv import load_dotenv, set_key

from clients.base_client import BaseClient
from config.api_routes import APIRoutes
import allure
from httpx import Response
from typing import Optional

logger = get_logger(__name__)

class TodosClient(BaseClient):
    """
    Клиент для работы с эндпоинтом /todos API_CHALLENGES.
    """
    def __init__(self, client):
        super().__init__(client)

    @allure.step("Get all todos")
    def get_all_todos(self, headers: Optional[dict[str, str]] = None, params: Optional[dict[str, str]] = None) -> Response:
        """
        Получает список всех задач.

        Args:
            headers: Дополнительные заголовки для запроса (переопределяют дефолтные).
            params: Query-параметры для запроса.
        """
        return self.get(APIRoutes.TODOS.value, headers=headers, params=params)


