from typing import Dict, Any, List
from tools.logger import get_logger
from httpx import Response
from pydantic import BaseModel, ValidationError
from tools.assertions.base_assertions import BaseResponseAsserts
from tools.assertions.schema.todos_model import TodosSchema
from tools.assertions.schema.xsd_paths import XSDPaths
import allure
import json
import xml.etree.ElementTree as ET

logger = get_logger(__name__)

class TodosAsserts(BaseResponseAsserts):
    """
    Класс для расширенных проверок эндпоинта "/todos".

    Наследуется от BaseResponseAsserts, предоставляет дополнительные проверки для API задач.
    """
    # Указание Pydantic-схемы для валидации JSON-ответов
    schema = TodosSchema
    # Путь к XSD-файлу для валидации XML-ответов
    xsd_path = XSDPaths.TODOS_XSD.path

    @allure.step("Check request query filter")
    def check_query_filter(self, response: Response, params: Dict[str, Any]):
        """
        Проверяет, что для каждого ключа либо все найденные значения совпадают с ожидаемым,
        либо ключ вовсе отсутствует в ответе.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param params: Словарь с ключами и их ожидаемыми значениями
        :raises AssertionError: Если ключ найден, но значения не совпадают с ожидаемым,
                                или если найдены значения, когда они не ожидались
        """
        logger.info(f"Starting query filter check with parameters: {params}")
        allure.attach(
            str(params),
            name="Параметры для проверки фильтрации",
            attachment_type=allure.attachment_type.TEXT
        )
        try:
            values = self.get_all_key_values(response=response, data_keys_to_extract=params)
            logger.debug(f"Extracted values from response: {values}")
            allure.attach(
                str(values),
                name="Извлеченные значения из ответа",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            logger.error(f"Failed to extract values from response: {e}")
            allure.attach(
                response.text,
                name="Ответ, вызвавший ошибку извлечения",
                attachment_type=allure.attachment_type.TEXT
            )
            raise # Перевыброс исключения, чтобы тест провалился

        with allure.step("Compare found values with expected"):
            for key, expected_value in params.items():
                found_data_list: List[Any] = values.get(key, [])

                allure.attach(
                    f"Ключ: '{key}', Ожидаемое значение: '{expected_value}', Найденные значения: {found_data_list}",
                    name=f"Детали проверки для ключа '{key}'",
                    attachment_type=allure.attachment_type.TEXT
                )
                logger.info(f"Checking key '{key}'. Expected: '{expected_value}'. Found: {found_data_list}")

                if found_data_list:
                    # Проверяем, что каждое найденное значение совпадает с ожидаемым
                    for found_value in found_data_list:
                        if found_value == expected_value:
                            logger.debug(f"Value '{found_value}' for key '{key}' matches expected '{expected_value}'")
                        else:
                            error_message = f"Mismatch for key '{key}': found value '{found_value}', but expected '{expected_value}'."
                            logger.error(error_message)
                            allure.attach(
                                f"Несоответствие! {error_message}",
                                name=f"Ошибка для ключа '{key}'",
                                attachment_type=allure.attachment_type.TEXT
                            )
                            raise AssertionError(error_message)
                else:
                    logger.debug(f"No values found for key '{key}'. This is acceptable as per 'or none' condition")

        logger.info("Query filter check completed successfully")

