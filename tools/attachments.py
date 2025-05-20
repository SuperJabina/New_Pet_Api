import json
from httpx import Response
import allure
from typing import Any, Dict, List
import xml.etree.ElementTree as ET


def attach_request_to_allure(method: str, url: str, headers: Dict[str, str], **kwargs: Any) -> None:
    """
    Прикрепляет данные запроса к Allure-отчету.
    """
    allure.attach(f"{method} {url}", name="Request", attachment_type=allure.attachment_type.TEXT)
    if headers:
        allure.attach(
            "\n".join(f"{k}: {v}" for k, v in headers.items()),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )
    if "json" in kwargs and kwargs["json"] is not None:
        allure.attach(
            json.dumps(kwargs["json"], indent=2, ensure_ascii=False),
            name="Request Body (JSON)",
            attachment_type=allure.attachment_type.JSON
        )
    if "params" in kwargs and kwargs["params"]:
        allure.attach(
            str(kwargs["params"]),
            name="Request Query Params",
            attachment_type=allure.attachment_type.TEXT
        )


def format_xml(xml_string: str, indent: str = "    ") -> str:
    """
    Форматирует XML-строку с отступами для читаемости.
    """
    try:
        # Парсим XML
        root = ET.fromstring(xml_string)

        def pretty_print(elem: ET.Element, level: int = 0) -> List[str]:
            """
            Рекурсивно форматирует XML-элемент с отступами.
            """
            lines: List[str] = []
            indent_str = indent * level
            # Открывающий тег
            tag_attrs = "".join(f' {k}="{v}"' for k, v in sorted(elem.attrib.items()))
            lines.append(f"{indent_str}<{elem.tag}{tag_attrs}>")

            # Текст внутри тега
            if elem.text and elem.text.strip():
                lines.append(f"{indent_str}{indent}{elem.text.strip()}")

            # Дочерние элементы
            for child in elem:
                lines.extend(pretty_print(child, level + 1))

            # Закрывающий тег
            if not elem.text or not elem.text.strip():
                if not elem:
                    lines[-1] = lines[-1][:-1] + "/>"  # Пустой тег: <tag/>
                else:
                    lines.append(f"{indent_str}</{elem.tag}>")
            else:
                lines.append(f"{indent_str}</{elem.tag}>")

            return lines

        # Собираем форматированный XML
        formatted_lines: List[str] = [r'<?xml version="1.0" encoding="utf-8"?>'] + pretty_print(root)
        return "\n".join(formatted_lines)
    except ET.ParseError:
        # Если XML невалидный, возвращаем исходную строку
        return xml_string


def attach_response_to_allure(response: Response, method: str, url: str) -> None:
    """
    Прикрепляет данные ответа к Allure-отчету.
    """
    allure.attach(
        f"HTTP/{response.http_version} {response.status_code} {response.reason_phrase}",
        name="Response Status",
        attachment_type=allure.attachment_type.TEXT
    )
    if response.headers:
        headers_dict = dict(response.headers)  # Явное преобразование в Dict[str, str]
        allure.attach(
            "\n".join(f"{k}: {v}" for k, v in headers_dict.items()),
            name="Response Headers",
            attachment_type=allure.attachment_type.TEXT
        )
    if response.text:
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            allure.attach(
                response.text,
                name="Response Body (JSON)",
                attachment_type=allure.attachment_type.JSON
            )
        elif "xml" in content_type:
            formatted_xml = format_xml(response.text)
            allure.attach(
                formatted_xml,
                name="Response Body (XML)",
                attachment_type=allure.attachment_type.XML
            )
        else:
            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.TEXT
            )