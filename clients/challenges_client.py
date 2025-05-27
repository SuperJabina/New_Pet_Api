import os
from tools.logger import get_logger
from dotenv import load_dotenv, set_key

from clients.base_client import BaseClient
from config.api_routes import APIRoutes
import allure
from httpx import Response
from typing import Optional

logger = get_logger(__name__)

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

    @allure.step("Get new token")
    def generate_new_challenger(self) -> Response:
        """
        Получает новый токен для заданий и сохраняет его в .env.
        :return: Возвращает ответ без тела, с заголовком X-CHALLENGER, содержащим токен
        """
        response = self.post(APIRoutes.NEW_TOKEN.value, headers={"X-CHALLENGER" : ""})
        if response.status_code == 201:
            token = response.headers.get("X-CHALLENGER")
            if token:
                logger.info(f"Successfully received token: {token[:10]}...")  # Логируем часть токена для безопасности
                # Путь к .env в корне проекта
                env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
                # Нормализуем путь для кросс-платформенности
                env_file = os.path.normpath(env_file)
                # Загружаем текущие переменные (если .env существует)
                try:
                    load_dotenv(env_file)
                    # Обновляем или добавляем API_X_CHALLENGER
                    set_key(env_file, "API_X_CHALLENGER", token)
                    # Обновляем os.environ для текущей сессии
                    os.environ["API_X_CHALLENGER"] = token
                except Exception as e:
                    logger.error(f"Failed to save token to .env or update os.environ: {e}")
            else:
                err = "Received successful response, but 'X-CHALLENGER' header is missing."
                logger.warning(err)
                allure.attach(err, name="Header is missing", attachment_type=allure.attachment_type.TEXT)
        else:
            err = f"Failed to get new token. Status Code: {response.status_code}"
            logger.error(err)
            allure.attach(err, name="Failed to get token", attachment_type=allure.attachment_type.TEXT)
        return response
