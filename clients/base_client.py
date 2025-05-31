import json
import os

import allure
import httpx
from httpx import Client, Response, QueryParams
from pydantic_core import Url
from typing import Union, Optional, Dict, List, Any
from tools.logger import get_logger
from tools.attachments import attach_request_to_allure, attach_response_to_allure
import xml.etree.ElementTree as ET

logger = get_logger(__name__)

class BaseClient:
    """
    Базовый клиент для выполнения HTTP-запросов с логированием и Allure-отчетами.

    Предоставляет методы для отправки запросов и обработки ответов.
    """
    def __init__(self, client: Client):
        self._endpoint = None
        self.client = client
        logger.info("BaseClient initialized with provided HTTP client")

    def _request(self, method: str, url: Union[Url, str], **kwargs) -> Response:
        """
        Внутренний метод для выполнения HTTP-запроса с логированием и Allure-отчетами.

        :param method: HTTP-метод (GET, POST, HEAD и т.д.)
        :param url: URL для запроса (строка или объект Url)
        :param kwargs: Дополнительные параметры запроса (заголовки, параметры и т.д.)
        :return: Объект Response с результатом запроса
        """
        # Получение токена X-Challenger из переменных окружения
        current_x_challenger = os.environ.get("API_X_CHALLENGER", "")
        headers: Optional[Dict[str, str]] = kwargs.pop("headers", None)
        # Нормализация заголовков клиента (приведение ключей к нижнему регистру)
        request_headers = {k.lower(): v for k, v in self.client.headers.items()}

        # Добавление или удаление токена X-Challenger в заголовках
        if current_x_challenger:
            request_headers["x-challenger"] = current_x_challenger
        elif "x-challenger" in request_headers: # Если токен стал пустой, удаляем старый
             del request_headers["x-challenger"]

        # Обновление заголовков переданными значениями, если они есть
        if headers is not None:
            request_headers.update({k.lower(): v for k, v in headers.items()})
            logger.debug(f"Headers updated with custom values: {headers}")

        logger.info(f"Make {method} request to {url} with headers {request_headers} params {kwargs.get('params', {})}")
        attach_request_to_allure(method=method, url=str(url), headers=request_headers, **kwargs)

        # Выполнение HTTP-запроса
        response = self.client.request(method, url, headers=request_headers, **kwargs)

        logger.info(f"Received response with status {response.status_code} from {url}")
        attach_response_to_allure(response, method=method, url=str(url))
        return response

    def get(self, url: Union[Url, str], params: QueryParams | None = None, headers: Dict[str, str] | None = None) -> Response:
        """
        Выполняет GET-запрос к указанному URL.

        :param url: URL для запроса (строка или объект Url)
        :param params: Параметры запроса (опционально)
        :param headers: Дополнительные HTTP-заголовки (опционально)
        :return: Объект Response с результатом запроса
        """
        logger.debug(f"Preparing GET request to {url} with params {params}")
        return self._request("GET", url, params=params, headers=headers)

    def post(self, url: Union[Url, str], data: Optional[Any] = None,
             headers: Optional[Dict[str, str]] = None) -> Response:
        """
        Выполняет POST-запрос к указанному URL с поддержкой JSON или XML в теле.

        :param url: URL для запроса (строка или объект Url)
        :param data: Данные для тела запроса (словарь для JSON или строка для XML, опционально)
        :param headers: Дополнительные HTTP-заголовки (опционально). Content-Type определяет тип данных
        :return: Объект Response с результатом запроса
        :raises ValueError: Если Content-Type не указан или не поддерживается для переданных данных
        """
        # Логирование подготовки POST-запроса
        logger.info(f"Preparing POST request to {url}")

        # Инициализация словаря для аргументов запроса и заголовков
        request_kwargs = {}
        headers = headers or {}

        # Проверка наличия данных
        if data is not None:
            # Определение Content-Type из заголовков (приведение к нижнему регистру для единообразия)
            content_type = next((v.lower() for k, v in headers.items() if k.lower() == "content-type"), None)

            # Обработка JSON-данных
            if content_type == "application/json" or (content_type is None and isinstance(data, (dict, list))):
                try:
                    # Проверяем, что данные могут быть сериализованы как JSON
                    json.dumps(data)
                    request_kwargs["json"] = data
                    headers["Content-Type"] = "application/json"
                    logger.debug(f"Adding JSON data to request body: {data}")
                except (TypeError, ValueError) as e:
                    logger.error(f"Invalid JSON data provided: {e}")
                    raise ValueError(f"Data cannot be serialized as JSON: {e}")

            # Обработка XML-данных
            elif content_type == "application/xml" or (content_type is None and isinstance(data, str)):
                try:
                    # Проверяем, что строка является валидным XML
                    ET.fromstring(data)
                    request_kwargs["content"] = data.encode("utf-8")  # Передаем XML как байты
                    headers["Content-Type"] = "application/xml"
                    logger.debug(
                        f"Adding XML data to request body: {data[:100]}...")  # Первые 100 символов для безопасности
                except ET.ParseError as e:
                    logger.error(f"Invalid XML data provided: {e}")
                    raise ValueError(f"Data is not valid XML: {e}")

            # Обработка неподдерживаемого Content-Type или данных
            else:
                logger.error(
                    f"Unsupported or missing Content-Type for data. Content-Type: {content_type}, data type: {type(data)}")
                raise ValueError(
                    f"Unsupported Content-Type '{content_type}' or data type {type(data)}. "
                    "Use 'application/json' for dict/list or 'application/xml' for string."
                )
        else:
            logger.debug("No data provided for POST request body")

        # Логирование заголовков
        logger.debug(f"Request headers: {headers}")

        try:
            # Выполнение POST-запроса через внутренний метод _request
            response = self._request("POST", url, headers=headers, **request_kwargs)
            logger.info(f"POST request completed with status code: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Failed to execute POST request to {url}: {e}")
            raise

    def head(self, url: Union[Url, str], json: dict | None = None, headers: Dict[str, str] | None = None) -> Response:
        """
        Выполняет HEAD-запрос к указанному URL.

        :param url: URL для запроса (строка или объект Url)
        :param json: JSON-данные для тела запроса (опционально)
        :param headers: Дополнительные HTTP-заголовки (опционально)
        :return: Объект Response с результатом запроса
        """
        logger.debug(f"Preparing HEAD request to {url} with JSON data {json}")
        return self._request("HEAD", url, json=json, headers=headers)

    @allure.step("Get available IDs")
    def get_available_ids(self, headers: Optional[Dict[str, str]] = None) -> List[Any]:
        """
        Выполняет GET-запрос к endpoint и извлекает все значения 'id' из ответа.

        :param headers: Дополнительные HTTP-заголовки (например, {'Accept': 'application/json'})
        :return: Список значений 'id' из JSON или XML ответа
        :raises ValueError: Если endpoint не определен или ответ некорректен
        :raises httpx.HTTPStatusError: Если запрос завершился ошибкой
        """
        # Проверка наличия endpoint
        if not self._endpoint:
            logger.error("Endpoint not defined in client")
            raise ValueError("Endpoint not defined in client")

        # Формирование URL с удалением начального слэша
        endpoint = self._endpoint.lstrip('/')
        logger.debug(f"Preparing to fetch IDs from endpoint: /{endpoint}")

        # Выполнение GET-запроса
        try:
            response = self.get(f"/{endpoint}", headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise

        # Определение типа содержимого ответа
        content_type = response.headers.get("content-type", "").lower()
        ids: List[Any] = []

        # Обработка JSON-ответа
        if "application/json" in content_type:
            try:
                data = response.json()
                logger.debug("Parsing JSON response for IDs")

                def extract_ids(json_data: Any, ids_list: List[Any]) -> None:
                    if isinstance(json_data, dict):
                        if "id" in json_data:
                            ids_list.append(json_data["id"])
                        for value in json_data.values():
                            extract_ids(value, ids_list)
                    elif isinstance(json_data, list):
                        for item in json_data:
                            extract_ids(item, ids_list)

                extract_ids(data, ids)
            except ValueError as e:
                allure.attach(
                    response.text,
                    name="Invalid JSON",
                    attachment_type=allure.attachment_type.JSON
                )
                logger.error(f"JSON parsing error: {e}")
                raise ValueError(f"Response is not valid JSON: {e}")
        # Обработка XML-ответа
        elif "application/xml" in content_type:
            try:
                root = ET.fromstring(response.text)
                id_elements = root.findall(".//id")
                ids = [elem.text or "" for elem in id_elements]
                logger.debug("Parsing XML response for IDs")
            except ET.ParseError as e:
                # Прикрепление некорректного XML к Allure и логирование ошибки
                allure.attach(
                    response.text,
                    name="Invalid XML",
                    attachment_type=allure.attachment_type.TEXT
                )
                logger.error(f"XML parsing error: {e}")
                raise ValueError(f"Response is not valid XML: {e}")
        # Обработка неподдерживаемого типа содержимого
        else:
            logger.error(f"Unsupported content type: {content_type}")
            raise ValueError(f"Unsupported content type: {content_type}")

        # Логирование и прикрепление извлеченных ID к Allure
        logger.debug(f"Extracted IDs: {ids}")
        allure.attach(
            str(ids),
            name="Extracted IDs",
            attachment_type=allure.attachment_type.TEXT
        )
        logger.info(f"Successfully extracted {len(ids)} IDs from response")
        return ids
