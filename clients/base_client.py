from httpx import Client, Response, QueryParams
from pydantic_core import Url
from typing import Union, Optional, Dict
from tools.logger import get_logger
from tools.attachments import attach_request_to_allure, attach_response_to_allure

class BaseClient:
    """
    Базовый клиент для выполнения HTTP-запросов с логированием и Allure-отчетами.
    """
    def __init__(self, client: Client):
        self.client = client
        self.logger = get_logger(__name__)

    def _request(self, method: str, url: Union[Url, str], **kwargs) -> Response:
        headers: Optional[Dict[str, str]] = kwargs.pop("headers", None)
        # Начинаем с заголовков по умолчанию из client, нормализуя ключи
        request_headers = {k.lower(): v for k, v in self.client.headers.items()}
        if headers is not None:
            # Обновляем заголовки, нормализуя ключи переданных headers
            request_headers.update({k.lower(): v for k, v in headers.items()})

        self.logger.info(f"Make {method} request to {url} with headers {request_headers} params {kwargs.get('params', {})}")
        attach_request_to_allure(method=method, url=str(url), headers=request_headers, **kwargs)

        response = self.client.request(method, url, headers=request_headers, **kwargs)

        self.logger.info(f"Got response {response.status_code} from {url}")
        attach_response_to_allure(response, method=method, url=str(url))
        return response

    def get(self, url: Union[Url, str], params: QueryParams | None = None, headers: Dict[str, str] | None = None) -> Response:
        return self._request("GET", url, params=params, headers=headers)

    def post(self, url: Union[Url, str], json: dict | None = None, headers: Dict[str, str] | None = None) -> Response:
        return self._request("POST", url, json=json, headers=headers)