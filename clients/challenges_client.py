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

    Наследуется от BaseClient, предоставляет методы для взаимодействия с API заданий.
    """
    def __init__(self, client):
        super().__init__(client)
        # Установка эндпоинта для работы с API заданиями
        self._endpoint = APIRoutes.CHALLENGES.value
        logger.info("ChallengesClient initialized with endpoint: " + self._endpoint)

    @allure.step("Get all challenges")
    def get_challenges_api(self, headers: Optional[dict[str, str]] = None, params: Optional[dict[str, str]] = None) -> Response:
        """
        Получает список всех заданий.

        :param headers: Дополнительные заголовки для запроса (переопределяют дефолтные)
        :param params: Query-параметры для запроса
        :return: Объект Response с результатом запроса
        """
        logger.info("Fetching all challenges from API")
        logger.debug(f"Request parameters - headers: {headers}, params: {params}")
        try:
            # Выполнение GET-запроса к эндпоинту заданий
            response = self.get(APIRoutes.CHALLENGES.value, headers=headers, params=params)
            logger.info(f"Successfully fetched challenges, status code: {response.status_code}")
            return response
        except Exception as e:
            # Логирование ошибки при выполнении запроса
            logger.error(f"Failed to fetch challenges: {e}")
            raise

    @allure.step("Get new token")
    def generate_new_challenger(self) -> Response:
        """
        Получает новый токен для заданий и сохраняет его в .env.

        :return: Возвращает ответ без тела, с заголовком X-CHALLENGER, содержащим токен
        """
        logger.info("Generating new challenger token")
        try:
            # Выполнение POST-запроса для получения нового токена
            response = self.post(APIRoutes.NEW_TOKEN.value, headers={"X-CHALLENGER": ""})
            logger.debug(f"Received response with status code: {response.status_code}")

            # Проверка успешности запроса (статус 201)
            if response.status_code == 201:
                token = response.headers.get("X-CHALLENGER")
                if token:
                    # Логирование успешного получения токена (часть для безопасности)
                    logger.info(f"Successfully received token: {token[:10]}...")
                    # Путь к .env в корне проекта
                    env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
                    # Нормализуем путь для кросс-платформенности
                    env_file = os.path.normpath(env_file)
                    logger.debug(f"Using .env file path: {env_file}")

                    # Загружаем текущие переменные и обновляем токен
                    try:
                        load_dotenv(env_file)
                        # Обновляем или добавляем API_X_CHALLENGER в .env
                        set_key(env_file, "API_X_CHALLENGER", token)
                        # Обновляем os.environ для текущей сессии
                        os.environ["API_X_CHALLENGER"] = token
                        logger.info("Token successfully saved to .env and updated in os.environ")
                    except Exception as e:
                        # Логирование ошибки при сохранении токена
                        logger.error(f"Failed to save token to .env or update os.environ: {e}")
                        raise
                else:
                    # Логирование и прикрепление предупреждения об отсутствии заголовка
                    err = "Received successful response, but 'X-CHALLENGER' header is missing."
                    logger.warning(err)
                    allure.attach(err, name="Header is missing", attachment_type=allure.attachment_type.TEXT)
            else:
                # Логирование и прикрепление ошибки при неудачном запросе
                err = f"Failed to get new token. Status Code: {response.status_code}"
                logger.error(err)
                allure.attach(err, name="Failed to get token", attachment_type=allure.attachment_type.TEXT)
            return response
        except Exception as e:
            # Логирование общей ошибки при генерации токена
            logger.error(f"Failed to generate new challenger token: {e}")
            raise
