from tools.logger import get_logger
from clients.base_client import BaseClient
from config.api_routes import APIRoutes
import allure
from httpx import Response
from typing import Optional

logger = get_logger(__name__)

class TodosClient(BaseClient):
    """
    Клиент для работы с эндпоинтом /todos API_CHALLENGES.

    Наследуется от BaseClient, предоставляет методы для взаимодействия с API задач.
    """
    def __init__(self, client):
        super().__init__(client)
        # Установка эндпоинта для работы с API задач
        self._endpoint = APIRoutes.TODOS.value
        logger.info("TodosClient initialized with endpoint: " + self._endpoint)

    @allure.step("Get all todos")
    def get_all_todos(self, headers: Optional[dict[str, str]] = None, params: Optional[dict[str, str]] = None) -> Response:
        """
        Получает список всех задач.

        :param headers: Дополнительные заголовки для запроса (переопределяют дефолтные)
        :param params: Query-параметры для запроса
        :return: Объект Response с результатом запроса
        """
        try:
            # Выполнение GET-запроса к эндпоинту задач
            response = self.get(APIRoutes.TODOS.value, headers=headers, params=params)
            logger.info(f"Successfully fetched all todos, status code: {response.status_code}")
            return response
        except Exception as e:
            # Логирование ошибки при выполнении запроса
            logger.error(f"Failed to fetch all todos: {e}")
            raise

    @allure.step("Get specific todo")
    def get_specific_todo(self, todo_id: int, headers: Optional[dict[str, str]] = None) ->Response:
        """
        Получает конкретную задачу по её ID.

        :param todo_id: ID получаемой записи
        :param headers: Дополнительные заголовки для запроса (переопределяют дефолтные)
        :return: Объект Response с результатом запроса
        """
        logger.info(f"Fetching specific todo with ID: {todo_id}")
        logger.debug(f"Request parameters - headers: {headers}")
        try:
            # Формирование URL для запроса конкретной задачи
            url = f"{APIRoutes.TODOS.value}/{todo_id}"
            # Выполнение GET-запроса
            response = self.get(url, headers=headers)
            logger.info(f"Successfully fetched todo with ID {todo_id}, status code: {response.status_code}")
            return response
        except Exception as e:
            # Логирование ошибки при выполнении запроса
            logger.error(f"Failed to fetch todo with ID {todo_id}: {e}")
            raise


