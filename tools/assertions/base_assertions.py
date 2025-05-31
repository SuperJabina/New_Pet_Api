from httpx import Response
import allure
import json
from typing import Dict, List, Any, Optional, Type
from pydantic import BaseModel, ValidationError
import xml.etree.ElementTree as ET
from lxml import etree
from tools.logger import get_logger
from tools.assertions.schema.xsd_paths import XSDPaths

logger = get_logger(__name__)

class BaseResponseAsserts:
    """
    Базовый класс для проверок HTTP-ответов с Allure-отчетами.

    Содержит методы для проверки статус-кодов, времени ответа, заголовков, тела и схем.
    """
    schema: Optional[Type[BaseModel]] = None
    xsd_path: Optional[str] = None

    @allure.step("Check status code is {expected_status}")
    def assert_status_code(self, response: Response, expected_status: int) -> None:
        """
        Проверяет, что статус-код ответа равен ожидаемому.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param expected_status: Ожидаемый статус-код
        :raises AssertionError: Если статус-код не совпадает с ожидаемым
        """
        logger.info(f"Checking status code, expected: {expected_status}")
        actual_status = response.status_code
        if actual_status != expected_status:
            logger.error(f"Status code mismatch: expected {expected_status}, got {actual_status}")
            allure.attach(
                f"Expected: {expected_status}\nActual: {actual_status}",
                name="Status Code Mismatch",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Expected status code {expected_status}, got {actual_status}")
        logger.debug(f"Status code check passed: {actual_status}")

    @allure.step("Check response time is less than {max_time} seconds")
    def assert_response_time(self, response: Response, max_time: float) -> None:
        """
        Проверяет, что время отклика меньше указанного порога (в секундах).

        :param response: Объект HTTP-ответа (httpx.Response)
        :param max_time: Максимально допустимое время ответа в секундах
        :raises AssertionError: Если время ответа превышает порог
        """
        logger.info(f"Checking response time, max allowed: {max_time}s")
        elapsed_time = response.elapsed.total_seconds()
        allure.attach(
            f"Response time: {elapsed_time:.3f}s\nMax allowed: {max_time:.3f}s",
            name="Response Time",
            attachment_type=allure.attachment_type.TEXT
        )
        if elapsed_time > max_time:
            logger.error(f"Response time {elapsed_time:.3f}s exceeds max {max_time:.3f}s")
            allure.attach(
                f"Elapsed: {elapsed_time:.3f}s\nMax allowed: {max_time:.3f}s",
                name="Response Time Exceeded",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Response time {elapsed_time:.3f}s exceeds max {max_time:.3f}s")
        logger.debug(f"Response time check passed: {elapsed_time:.3f}s")

    @allure.step("Check headers present: {expected_headers}")
    def assert_headers_present(self, response: Response, expected_headers: List[str]) -> None:
        """
        Проверяет наличие указанных заголовков в ответе.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param expected_headers: Список ожидаемых заголовков
        :raises AssertionError: Если хотя бы один заголовок отсутствует
        """
        logger.info(f"Checking for presence of headers: {expected_headers}")
        missing_headers = [h for h in expected_headers if h.lower() not in response.headers]
        if missing_headers:
            logger.error(f"Headers not found: {missing_headers}")
            allure.attach(
                f"Missing headers: {missing_headers}\nAvailable headers: {list(response.headers.keys())}",
                name="Missing Headers",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Headers not found: {missing_headers}")
        logger.debug(f"Header presence check passed for: {expected_headers}")

    @allure.step("Check header values: {expected_headers}")
    def assert_header_values(self, response: Response, expected_headers: Dict[str, str]) -> None:
        """
        Проверяет значения указанных заголовков в ответе.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param expected_headers: Словарь с ожидаемыми заголовками и их значениями
        :raises AssertionError: Если значения заголовков не совпадают
        """
        logger.info(f"Checking header values: {expected_headers}")
        mismatches = []
        for header, expected_value in expected_headers.items():
            actual_value = response.headers.get(header.lower())
            if actual_value != expected_value:
                mismatches.append(f"{header}: expected '{expected_value}', got '{actual_value}'")
        if mismatches:
            logger.error(f"Header value mismatches: {mismatches}")
            allure.attach(
                "\n".join(mismatches),
                name="Header Value Mismatches",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Header value mismatches:\n{'\n'.join(mismatches)}")
        logger.debug(f"Header values check passed for: {expected_headers}")

    @allure.step("Check body keys present: {expected_keys}")
    def assert_body_keys_present(self, response: Response, expected_keys: List[str]) -> None:
        """
        Проверяет наличие указанных ключей в теле ответа (JSON).

        :param response: Объект HTTP-ответа (httpx.Response)
        :param expected_keys: Список ожидаемых ключей в JSON
        :raises AssertionError: Если JSON невалидный или ключи отсутствуют
        """
        logger.info(f"Checking for presence of body keys: {expected_keys}")
        try:
            body = response.json()
        except ValueError as e:
            logger.error(f"Response body is not JSON: {e}")
            raise AssertionError(f"Response body is not JSON: {e}")

        missing_keys = [k for k in expected_keys if k not in body]
        if missing_keys:
            logger.error(f"Body keys not found: {missing_keys}")
            allure.attach(
                f"Missing keys: {missing_keys}\nAvailable keys: {list(body.keys())}",
                name="Missing Body Keys",
                attachment_type=allure.attachment_type.JSON
            )
            raise AssertionError(f"Body keys not found: {missing_keys}")
        logger.debug(f"Body keys presence check passed for: {expected_keys}")

    @allure.step("Check body key values: {expected_values}")
    def assert_body_key_values(self, response: Response, expected_values: Dict[str, Any]) -> None:
        """
        Проверяет, что хотя бы одна запись в JSON-теле ответа содержит указанные ключи с ожидаемыми значениями.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param expected_values: Словарь с ключами и их ожидаемыми значениями
        :raises AssertionError: Если JSON невалидный или ни одна запись не содержит ожидаемого значения
        """
        logger.info(f"Checking body key values: {expected_values}")
        try:
            body = response.json()
        except ValueError as e:
            logger.error(f"Response body is not valid JSON: {e}")
            allure.attach(
                response.text,
                name="Invalid JSON",
                attachment_type=allure.attachment_type.JSON
            )
            raise AssertionError(f"Response body is not valid JSON: {e}")

        def find_key_values(data: Any, key: str, matches: List[Any]) -> None:
            """
            Рекурсивно ищет все вхождения ключа в JSON и собирает их значения.

            :param data: Текущий JSON-объект (dict, list и т.д.)
            :param key: Искомый ключ
            :param matches: Список для хранения найденных значений
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
            logger.error(f"Body key value mismatches: {mismatches}")
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
        logger.debug(f"Body key values check passed for: {expected_values}")

    def assert_json_schema(self, response: Response, schema: type[BaseModel]) -> None:
        """
        Проверяет, что тело ответа соответствует указанной Pydantic-схеме.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param schema: Класс Pydantic-схемы для валидации
        :raises AssertionError: Если JSON невалидный или не соответствует схеме
        :raises TypeError: Если schema не является классом Pydantic
        """
        logger.info(f"Validating JSON schema: {schema.__name__}")
        if not isinstance(schema, type) or not issubclass(schema, BaseModel):
            logger.error(f"Invalid schema type: expected Pydantic model, got {type(schema).__name__}")
            raise TypeError(f"Expected Pydantic model class, got {type(schema).__name__}")

        try:
            body = response.json()
        except ValueError as e:
            logger.error(f"Response body is not JSON: {e}")
            raise AssertionError(f"Response body is not JSON: {e}")

        with allure.step(f"Validate JSON schema: {schema.__name__}"):
            try:
                schema(**body)
                logger.debug(f"JSON schema validation passed for: {schema.__name__}")
            except ValidationError as e:
                logger.error(f"Schema validation failed: {e}")
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

        :param response: Объект HTTP-ответа (httpx.Response)
        :param expected_tags: Список имен тегов
        :raises AssertionError: Если XML невалидный или хотя бы один тег отсутствует
        """
        logger.info(f"Checking for presence of XML tags: {expected_tags}")
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logger.error(f"Response body is not valid XML: {e}")
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
            logger.error(f"XML tag presence check failed: {errors}")
            allure.attach(
                response.text,
                name="XML Body",
                attachment_type=allure.attachment_type.XML
            )
            raise AssertionError("\n".join(errors))
        logger.debug(f"XML tag presence check passed for: {expected_tags}")

    @allure.step("Check XML tag values: {tag_value_pairs}")
    def assert_xml_tag_value(self, response: Response, tag_value_pairs: Dict[str, Any]) -> None:
        """
        Проверяет, что хотя бы одно вхождение каждого тега в XML-теле ответа имеет ожидаемое значение.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param tag_value_pairs: Словарь с тегами и их ожидаемыми значениями
        :raises AssertionError: Если XML невалидный, тег отсутствует или ни одно значение не совпадает
        """
        logger.info(f"Checking XML tag values: {tag_value_pairs}")
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logger.error(f"Response body is not valid XML: {e}")
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
            logger.error(f"XML tag value mismatches: {errors}")
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
        logger.debug(f"XML tag values check passed for: {tag_value_pairs}")

    @allure.step("Validate XML schema: {xsd_file}")
    def assert_xml_schema(self, response: Response, xsd_file: str = XSDPaths.CHALLENGES_XSD.path) -> None:
        """
        Проверяет, что XML-тело ответа соответствует указанной XSD-схеме.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param xsd_file: Путь к XSD-файлу
        :raises AssertionError: Если XML невалидный или не соответствует схеме
        """
        logger.info(f"Validating XML schema with file: {xsd_file}")
        try:
            xml_doc = etree.fromstring(response.text.encode("utf-8"))
        except etree.ParseError as e:
            logger.error(f"Response body is not valid XML: {e}")
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
            logger.debug("XML schema validation passed")
        except (etree.DocumentInvalid, IOError, etree.ParseError) as e:
            logger.error(f"XML does not match schema: {e}")
            allure.attach(
                response.text,
                name="Invalid XML Schema",
                attachment_type=allure.attachment_type.XML
            )
            raise AssertionError(f"XML does not match schema: {e}")

    def get_all_key_values(self, response: Response, data_keys_to_extract: Dict[str, Any]):
        """
        Извлекает значения для заданных ключей из XML или JSON ответа.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param data_keys_to_extract: Словарь, где ключи - искомые теги/ключи
        :return: Словарь, где ключи - искомые теги/ключи, а значения - списки найденных значений
        :raises AssertionError: Если тело ответа невалидное (XML или JSON)
        """
        logger.info(f"Extracting key values: {data_keys_to_extract.keys()}")
        all_found_values: Dict[str, List[Any]] = {key: [] for key in data_keys_to_extract} # Инициализируем списки для каждого искомого ключа
        content_type = response.headers.get("content-type", "")
        logger.debug(f"Content type detected: {content_type}")
        if "application/xml" in content_type:
            try:
                root = ET.fromstring(response.text)
                for tag in data_keys_to_extract:
                    tag_elements = root.findall(f".//{tag}")
                    all_found_values[tag] = [elem.text or "" for elem in tag_elements]
                logger.debug(f"Extracted XML values: {all_found_values}")
            except ET.ParseError as e:
                logger.error(f"Response body is not valid XML: {e}")
                allure.attach(
                    response.text,
                    name="Invalid XML",
                    attachment_type=allure.attachment_type.TEXT
                )
                raise AssertionError(f"Response body is not valid XML: {e}")
        elif "application/json" in content_type:
            try:
                body = response.json()

                def _find_values_recursively(current_data: Any, target_key: str, found_list: List[Any]) -> None:
                    """
                    Рекурсивно ищет все вхождения target_key в JSON и собирает их значения.

                    :param current_data: Текущий JSON-объект (dict, list и т.д.)
                    :param target_key: Искомый ключ
                    :param found_list: Список для хранения найденных значений
                    """
                    if isinstance(current_data, dict):
                        if target_key in current_data:
                            found_list.append(current_data[target_key])
                        for value_in_dict in current_data.values():
                            _find_values_recursively(value_in_dict, target_key, found_list)
                    elif isinstance(current_data, list):
                        for item_in_list in current_data:
                            _find_values_recursively(item_in_list, target_key, found_list)

                for key_to_find in data_keys_to_extract:  # Итерируемся по ключам
                    _find_values_recursively(body, key_to_find, all_found_values[key_to_find])
                logger.debug(f"Extracted JSON values: {all_found_values}")
            except ValueError as e:
                logger.error(f"Response body is not valid JSON: {e}")
                allure.attach(
                    response.text,
                    name="Invalid JSON Response",
                    attachment_type=allure.attachment_type.JSON
                )
                raise AssertionError(f"Response body is not valid JSON: {e}")
        else:
            logger.warning(f"Unsupported content type: {content_type}. Skipping value extraction")
            allure.attach(
                response.text,
                name="Unsupported Content Type",
                attachment_type=allure.attachment_type.TEXT
            )
        logger.info(f"Key values extraction completed: {all_found_values}")
        return all_found_values

    def comprehensive_checks(self, response: Response, checks: Dict[str, Any]):
        """
        Выполняет комплексные проверки ответа API.

        :param response: Объект HTTP-ответа (httpx.Response)
        :param checks: Словарь с параметрами проверок
        :raises AssertionError: Если проверки не пройдены
        :raises ValueError: Если схема для валидации не определена
        """
        logger.info("Starting comprehensive checks for API response")
        logger.debug(f"Checks to perform: {checks}")

        try:
            if checks.get("status_code"):
                self.assert_status_code(response, checks["status_code"])
            if checks.get("response_time"):
                self.assert_response_time(response, max_time=checks["response_time"])
            if checks.get("headers_present"):
                self.assert_headers_present(response, checks["headers_present"])
            if checks.get("header_values"):
                self.assert_header_values(response, checks["header_values"])
            if response.is_success:
                is_xml = checks["request_headers"] is not None and checks["request_headers"].get(
                    "Accept") == "application/xml"
                if checks.get("schema"):
                    if is_xml:
                        self.assert_header_values(response, {"content-type": "application/xml"})
                        if self.xsd_path is not None:
                            self.assert_xml_schema(response, self.xsd_path)
                        else:
                            logger.error("XSD path not defined for XML schema validation")
                            raise ValueError("XSD path not defined for XML schema validation")
                    else:
                        self.assert_header_values(response, {"content-type": "application/json"})
                        if self.schema is not None:
                            self.assert_json_schema(response, self.schema)
                        else:
                            logger.error("Schema not defined for JSON schema validation")
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
            logger.info("Comprehensive checks completed successfully")
        except Exception as e:
            logger.error(f"Comprehensive checks failed: {e}")
            raise