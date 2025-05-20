from httpx import Response
import allure
import json
from typing import Dict, List, Any, Union


class BaseResponseAsserts:
    """
    Базовый класс для проверок HTTP-ответов с Allure-отчетами.
    """

    @staticmethod
    @allure.step("Check status code is {expected_status}")
    def assert_status_code(response: Response, expected_status: int) -> None:
        """
        Проверяет, что статус-код ответа равен ожидаемому.
        """
        actual_status = response.status_code
        if actual_status != expected_status:
            allure.attach(
                f"Expected: {expected_status}\nActual: {actual_status}",
                name="Status Code Mismatch",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Expected status code {expected_status}, got {actual_status}")

    @staticmethod
    @allure.step("Check response time is less than {max_time} seconds")
    def assert_response_time(response: Response, max_time: float) -> None:
        """
        Проверяет, что время отклика меньше указанного порога (в секундах).
        """
        elapsed_time = response.elapsed.total_seconds()
        allure.attach(
            f"Response time: {elapsed_time:.3f}s\nMax allowed: {max_time:.3f}s",
            name="Response Time",
            attachment_type=allure.attachment_type.TEXT
        )
        if elapsed_time > max_time:
            allure.attach(
                f"Elapsed: {elapsed_time:.3f}s\nMax allowed: {max_time:.3f}s",
                name="Response Time Exceeded",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Response time {elapsed_time:.3f}s exceeds max {max_time:.3f}s")

    @staticmethod
    @allure.step("Check headers present: {expected_headers}")
    def assert_headers_present(response: Response, expected_headers: List[str]) -> None:
        """
        Проверяет наличие указанных заголовков в ответе.
        """
        missing_headers = [h for h in expected_headers if h.lower() not in response.headers]
        if missing_headers:
            allure.attach(
                f"Missing headers: {missing_headers}\nAvailable headers: {list(response.headers.keys())}",
                name="Missing Headers",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Headers not found: {missing_headers}")

    @staticmethod
    @allure.step("Check header values: {expected_headers}")
    def assert_header_values(response: Response, expected_headers: Dict[str, str]) -> None:
        """
        Проверяет значения указанных заголовков в ответе.
        """
        mismatches = []
        for header, expected_value in expected_headers.items():
            actual_value = response.headers.get(header.lower())
            if actual_value != expected_value:
                mismatches.append(f"{header}: expected '{expected_value}', got '{actual_value}'")
        if mismatches:
            allure.attach(
                "\n".join(mismatches),
                name="Header Value Mismatches",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Header value mismatches:\n{'\n'.join(mismatches)}")

    @staticmethod
    @allure.step("Check body keys present: {expected_keys}")
    def assert_body_keys_present(response: Response, expected_keys: List[str]) -> None:
        """
        Проверяет наличие указанных ключей в теле ответа (JSON).
        """
        try:
            body = response.json()
        except ValueError as e:
            raise AssertionError(f"Response body is not JSON: {e}")

        missing_keys = [k for k in expected_keys if k not in body]
        if missing_keys:
            allure.attach(
                f"Missing keys: {missing_keys}\nAvailable keys: {list(body.keys())}",
                name="Missing Body Keys",
                attachment_type=allure.attachment_type.JSON
            )
            raise AssertionError(f"Body keys not found: {missing_keys}")

    @staticmethod
    @allure.step("Check body key values: {expected_values}")
    def assert_body_key_values(response: Response, expected_values: Dict[str, Any]) -> None:
        """
        Проверяет значения указанных ключей в теле ответа (JSON).
        """
        try:
            body = response.json()
        except ValueError as e:
            raise AssertionError(f"Response body is not JSON: {e}")

        mismatches = []
        for key, expected_value in expected_values.items():
            if key not in body:
                mismatches.append(f"{key}: key not found")
            elif body[key] != expected_value:
                mismatches.append(f"{key}: expected '{expected_value}', got '{body[key]}'")
        if mismatches:
            allure.attach(
                "\n".join(mismatches),
                name="Body Key Value Mismatches",
                attachment_type=allure.attachment_type.JSON
            )
            raise AssertionError(f"Body key value mismatches:\n{'\n'.join(mismatches)}")