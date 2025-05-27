from httpx import Response
import allure
import json
from typing import Dict, List, Any, Union, Optional, Type
from pydantic import BaseModel, ValidationError
import xml.etree.ElementTree as ET
from lxml import etree

from tools.assertions.schema.xsd_paths import XSDPaths


class BaseResponseAsserts:
    """
    Базовый класс для проверок HTTP-ответов с Allure-отчетами.
    """
    schema: Optional[Type[BaseModel]] = None
    xsd_path: Optional[str] = None

    @allure.step("Check status code is {expected_status}")
    def assert_status_code(self, response: Response, expected_status: int) -> None:
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

    @allure.step("Check response time is less than {max_time} seconds")
    def assert_response_time(self, response: Response, max_time: float) -> None:
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

    @allure.step("Check headers present: {expected_headers}")
    def assert_headers_present(self, response: Response, expected_headers: List[str]) -> None:
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

    @allure.step("Check header values: {expected_headers}")
    def assert_header_values(self, response: Response, expected_headers: Dict[str, str]) -> None:
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

    @allure.step("Check body keys present: {expected_keys}")
    def assert_body_keys_present(self, response: Response, expected_keys: List[str]) -> None:
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

    @allure.step("Check body key values: {expected_values}")
    def assert_body_key_values(self, response: Response, expected_values: Dict[str, Any]) -> None:
        """
        Проверяет, что хотя бы одна запись в JSON-теле ответа содержит указанные ключи с ожидаемыми значениями.
        :param response: Ответ HTTP (httpx.Response).
        :param expected_values: Словарь с ключами и их ожидаемыми значениями.
        :raises AssertionError: Если JSON невалидный или ни одна запись не содержит ожидаемого значения.
        """
        try:
            body = response.json()
        except ValueError as e:
            allure.attach(
                response.text,
                name="Invalid JSON",
                attachment_type=allure.attachment_type.JSON
            )
            raise AssertionError(f"Response body is not valid JSON: {e}")

        def find_key_values(data: Any, key: str, matches: List[Any]) -> None:
            """
            Рекурсивно ищет все вхождения ключа в JSON и собирает их значения.
            :param data: Текущий JSON-объект (dict, list, etc.).
            :param key: Искомый ключ.
            :param matches: Список для хранения найденных значений.
            """
            if isinstance(data, dict):
                if key in data:
                    matches.append(data[key])
                for value in data.values():
                    find_key_values(value, key, matches)
            elif isinstance(data, list):
                for item in data:
                    find_key_values(item, key, matches)

        mismatches = []
        for key, expected_value in expected_values.items():
            matches = []
            find_key_values(body, key, matches)
            if not matches:
                mismatches.append(f"{key}: key not found in any record")
            elif not any(actual_value == expected_value for actual_value in matches):
                mismatches.append(
                    f"{key}: expected '{expected_value}', found values {matches}"
                )

        if mismatches:
            allure.attach(
                "\n".join(mismatches),
                name="Body Key Value Mismatches",
                attachment_type=allure.attachment_type.JSON
            )
            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.JSON
            )
            raise AssertionError(f"Body key value mismatches:\n{'\n'.join(mismatches)}")

    def assert_json_schema(self, response: Response, schema: type[BaseModel]) -> None:
        """
        Проверяет, что тело ответа соответствует указанной Pydantic-схеме.
        """
        if not isinstance(schema, type) or not issubclass(schema, BaseModel):
            raise TypeError(f"Expected Pydantic model class, got {type(schema).__name__}")

        try:
            body = response.json()
        except ValueError as e:
            raise AssertionError(f"Response body is not JSON: {e}")

        with allure.step(f"Validate JSON schema: {schema.__name__}"):
            try:
                schema(**body)
            except ValidationError as e:
                allure.attach(
                    json.dumps(body, indent=2, ensure_ascii=False),
                    name="Invalid Data",
                    attachment_type=allure.attachment_type.JSON
                )
                allure.attach(
                    str(e),
                    name=f"Schema Validation Error - {schema.__name__}",
                    attachment_type=allure.attachment_type.TEXT
                )
                raise AssertionError(f"Schema validation failed: {e}")

    @allure.step("Check XML tags present: {expected_tags}")
    def assert_xml_tag_present(self, response: Response, expected_tags: List[str]) -> None:
        """
        Проверяет наличие всех указанных тегов в XML-теле ответа.
        :param response: Ответ HTTP (httpx.Response).
        :param expected_tags: Список имен тегов (List[str]).
        :raises AssertionError: Если XML невалидный или хотя бы один тег отсутствует.
        """
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            allure.attach(
                response.text,
                name="Invalid XML",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Response body is not valid XML: {e}")

        errors = []
        for tag in expected_tags:
            if root.tag != tag and not root.findall(f".//{tag}"):
                errors.append(f"XML tag '{tag}' not found in response")

        if errors:
            allure.attach(
                response.text,
                name="XML Body",
                attachment_type=allure.attachment_type.XML
            )
            raise AssertionError("\n".join(errors))

    @allure.step("Check XML tag values: {tag_value_pairs}")
    def assert_xml_tag_value(self, response: Response, tag_value_pairs: Dict[str, Any]) -> None:
        """
        Проверяет, что хотя бы одно вхождение каждого тега в XML-теле ответа имеет ожидаемое значение.
        :param response: Ответ HTTP (httpx.Response).
        :param tag_value_pairs: Словарь с тегами и их ожидаемыми значениями (Dict[str, str]).
        :raises AssertionError: Если XML невалидный, тег отсутствует или ни одно значение не совпадает.
        """
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            allure.attach(
                response.text,
                name="Invalid XML",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Response body is not valid XML: {e}")

        errors = []
        for tag, expected_value in tag_value_pairs.items():
            tag_elements = root.findall(f".//{tag}")
            if not tag_elements:
                errors.append(f"XML tag '{tag}' not found in response")
                continue
            actual_values = [elem.text or "" for elem in tag_elements]
            if not any(actual_value == str(expected_value) for actual_value in actual_values):
                errors.append(
                    f"XML tag '{tag}' has no value matching '{expected_value}', found values {actual_values}"
                )

        if errors:
            allure.attach(
                response.text,
                name="XML Body",
                attachment_type=allure.attachment_type.XML
            )
            allure.attach(
                "\n".join(errors),
                name="XML Tag Value Mismatches",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError("\n".join(errors))

    @allure.step("Validate XML schema: {xsd_file}")
    def assert_xml_schema(self, response: Response, xsd_file: str = XSDPaths.CHALLENGES_XSD.path) -> None:
        """
        Проверяет, что XML-тело ответа соответствует указанной XSD-схеме.
        :param response: Ответ HTTP (httpx.Response).
        :param xsd_file: Путь к XSD-файлу.
        :raises AssertionError: Если XML невалидный или не соответствует схеме.
        """
        try:
            xml_doc = etree.fromstring(response.text.encode("utf-8"))
        except etree.ParseError as e:
            allure.attach(
                response.text,
                name="Invalid XML",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Response body is not valid XML: {e}")

        try:
            with open(xsd_file, "rb") as f:
                schema_root = etree.parse(f)
                schema = etree.XMLSchema(schema_root)
            schema.assertValid(xml_doc)
            allure.attach(
                xsd_file,
                name="XSD Schema File",
                attachment_type=allure.attachment_type.TEXT
            )
        except (etree.DocumentInvalid, IOError, etree.ParseError) as e:
            allure.attach(
                response.text,
                name="Invalid XML Schema",
                attachment_type=allure.attachment_type.XML
            )
            raise AssertionError(f"XML does not match schema: {e}")

    def comprehensive_checks(self, response: Response, checks: Dict[str, Any]):
        """
        Выполняет комплексные проверки ответа API.
        :param response: Ответ HTTP (httpx.Response).
        :param checks: Словарь с параметрами проверок.
        :raises AssertionError: Если проверки не пройдены.
        """
        if checks.get("status_code"):
            self.assert_status_code(response, checks["status_code"])
        if checks.get("response_time"):
            self.assert_response_time(response, max_time=checks["response_time"])
        if checks.get("headers_present"):
            self.assert_headers_present(response, checks["headers_present"])
        if checks.get("header_values"):
            self.assert_header_values(response, checks["header_values"])
        if response.is_success:
            is_xml = checks["request_headers"] is not None and checks["request_headers"].get("Accept") == "application/xml"
            if checks.get("schema"):
                if is_xml:
                    self.assert_header_values(response, {"content-type": "application/xml"})
                    if self.xsd_path is not None:
                        self.assert_xml_schema(response, self.xsd_path)
                    else:
                        raise ValueError("XSD path not defined for XML schema validation")
                else:
                    self.assert_header_values(response, {"content-type": "application/json"})
                    if self.schema is not None:
                        self.assert_json_schema(response, self.schema)
                    else:
                        raise ValueError("Schema not defined for JSON schema validation")
            if checks.get("key_present"):
                if is_xml:
                    self.assert_xml_tag_present(response, checks["key_present"])
                else:
                    self.assert_body_keys_present(response, checks["key_present"])
            if checks.get("key_value"):
                if is_xml:
                    self.assert_xml_tag_value(response, checks["key_value"])
                else:
                    self.assert_body_key_values(response, checks["key_value"])