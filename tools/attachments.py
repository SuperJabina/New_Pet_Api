import json
from httpx import Response
import allure
from typing import Any, Dict, List
import xml.etree.ElementTree as ET
from tools.logger import get_logger

logger = get_logger(__name__)

def attach_request_to_allure(method: str, url: str, headers: Dict[str, str], **kwargs: Any) -> None:
    """
    Прикрепляет данные запроса к Allure-отчету с поддержкой JSON и XML.

    :param method: HTTP-метод запроса (GET, POST и т.д.)
    :param url: URL запроса
    :param headers: Заголовки запроса в виде словаря
    :param kwargs: Дополнительные параметры запроса (json, xml, params и т.д.)
    """
    logger.info(f"Attaching request data to Allure for {method} {url}")
    allure.attach(f"{method} {url}", name="Request", attachment_type=allure.attachment_type.TEXT)

    # Прикрепление заголовков запроса, если они есть
    if headers:
        logger.debug(f"Attaching request headers: {headers}")
        allure.attach(
            "\n".join(f"{k}: {v}" for k, v in headers.items()),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )

    # Определение типа контента из заголовков
    content_type = next((v.lower() for k, v in headers.items() if k.lower() == "content-type"), None)

    # Прикрепление тела запроса в формате JSON, если оно присутствует
    if "json" in kwargs and kwargs["json"] is not None and (content_type is None or "application/json" in content_type):
        logger.debug(f"Attaching JSON request body: {kwargs['json']}")
        try:
            allure.attach(
                json.dumps(kwargs["json"], indent=2, ensure_ascii=False),
                name="Request Body (JSON)",
                attachment_type=allure.attachment_type.JSON
            )
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize JSON data for Allure: {e}")
            allure.attach(
                str(kwargs["json"]),
                name="Invalid JSON Request Body",
                attachment_type=allure.attachment_type.TEXT
            )

    # Прикрепление тела запроса в формате XML, если оно присутствует
    if "xml" in kwargs and kwargs["xml"] is not None and (content_type is None or "application/xml" in content_type):
        logger.debug(f"Attaching XML request body: {kwargs['xml'][:100]}...")  # Первые 100 символов для безопасности
        try:
            # Форматирование XML с помощью функции format_xml
            formatted_xml = format_xml(kwargs["xml"])
            allure.attach(
                formatted_xml,
                name="Request Body (XML)",
                attachment_type=allure.attachment_type.XML
            )
        except Exception as e:
            logger.error(f"Failed to format XML data for Allure: {e}")
            allure.attach(
                kwargs["xml"],
                name="Invalid XML Request Body",
                attachment_type=allure.attachment_type.TEXT
            )

    # Прикрепление параметров запроса, если они есть
    if "params" in kwargs and kwargs["params"]:
        logger.debug(f"Attaching query params: {kwargs['params']}")
        allure.attach(
            str(kwargs["params"]),
            name="Request Query Params",
            attachment_type=allure.attachment_type.TEXT
        )

    # Логирование успешного завершения прикрепления
    logger.info("Request data successfully attached to Allure")

def format_xml(xml_string: str, indent: str = "    ") -> str:
    """
    Форматирует XML-строку с отступами для читаемости.

    :param xml_string: Исходная XML-строка
    :param indent: Символы отступа (по умолчанию 4 пробела)
    :return: Форматированная XML-строка или исходная при ошибке парсинга
    """
    logger.info("Starting XML formatting")
    try:
        # Парсим XML
        root = ET.fromstring(xml_string)
        logger.debug("XML string parsed successfully")

        def pretty_print(elem: ET.Element, level: int = 0) -> List[str]:
            """
            Рекурсивно форматирует XML-элемент с отступами.

            :param elem: XML-элемент для форматирования
            :param level: Уровень вложенности для отступов
            :return: Список строк с форматированным XML
            """
            lines: List[str] = []
            indent_str = indent * level
            # Формирование открывающего тега с атрибутами
            tag_attrs = "".join(f' {k}="{v}"' for k, v in sorted(elem.attrib.items()))
            lines.append(f"{indent_str}<{elem.tag}{tag_attrs}>")

            # Добавление текста внутри тега, если он есть
            if elem.text and elem.text.strip():
                lines.append(f"{indent_str}{indent}{elem.text.strip()}")

            # Рекурсивная обработка дочерних элементов
            for child in elem:
                lines.extend(pretty_print(child, level + 1))

            # Формирование закрывающего тега или пустого тега
            if not elem.text or not elem.text.strip():
                if not elem:
                    lines[-1] = lines[-1][:-1] + "/>"  # Пустой тег: <tag/>
                else:
                    lines.append(f"{indent_str}</{elem.tag}>")
            else:
                lines.append(f"{indent_str}</{elem.tag}>")

            return lines

        # Собираем форматированный XML с заголовком
        formatted_lines: List[str] = [r'<?xml version="1.0" encoding="utf-8"?>'] + pretty_print(root)
        formatted_xml = "\n".join(formatted_lines)
        logger.info("XML successfully formatted")
        return formatted_xml
    except ET.ParseError as e:
        # Логирование ошибки парсинга и возврат исходной строки
        logger.error(f"Failed to parse XML: {e}")
        return xml_string


def attach_response_to_allure(response: Response, method: str, url: str) -> None:
    """
    Прикрепляет данные ответа к Allure-отчету.

    :param response: Объект Response с данными HTTP-ответа
    :param method: HTTP-метод запроса
    :param url: URL запроса
    """
    logger.info(f"Attaching response data to Allure for {method} {url}")
    allure.attach(
        f"HTTP/{response.http_version} {response.status_code} {response.reason_phrase}",
        name="Response Status",
        attachment_type=allure.attachment_type.TEXT
    )

    # Прикрепление заголовков ответа, если они есть
    if response.headers:
        headers_dict = dict(response.headers)  # Явное преобразование в Dict[str, str]
        logger.debug(f"Attaching response headers: {headers_dict}")
        allure.attach(
            "\n".join(f"{k}: {v}" for k, v in headers_dict.items()),
            name="Response Headers",
            attachment_type=allure.attachment_type.TEXT
        )

    # Обработка тела ответа
    if response.text:
        content_type = response.headers.get("content-type", "").lower()
        logger.debug(f"Processing response body with content type: {content_type}")

        # Обработка JSON-ответа
        if "application/json" in content_type:
            try:
                # Форматируем JSON с отступами
                formatted_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
                logger.debug("JSON response body formatted successfully")
                allure.attach(
                    formatted_json,
                    name="Response Body (JSON)",
                    attachment_type=allure.attachment_type.JSON
                )
            except ValueError as e:
                # Прикрепление невалидного JSON как текста
                logger.error(f"Failed to parse JSON response: {e}")
                allure.attach(
                    response.text,
                    name="Response Body (Invalid JSON)",
                    attachment_type=allure.attachment_type.TEXT
                )

        # Обработка XML-ответа
        elif "xml" in content_type:
            formatted_xml = format_xml(response.text)
            logger.debug("XML response body formatted successfully")
            allure.attach(
                formatted_xml,
                name="Response Body (XML)",
                attachment_type=allure.attachment_type.XML
            )

        # Обработка прочих типов содержимого
        else:
            logger.debug("Attaching response body as plain text")
            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.TEXT
            )
    logger.info("Response data successfully attached to Allure")