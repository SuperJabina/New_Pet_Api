from httpx import Response
from pydantic import BaseModel, ValidationError
from tools.assertions.base_assertions import BaseResponseAsserts
import allure
import json
import xml.etree.ElementTree as ET


class ChallengesAsserts(BaseResponseAsserts):
    """
    Класс для проверок HTTP-ответов, включая валидацию JSON-схемы.
    Наследуется от BaseResponseAsserts.
    """

    @staticmethod
    def assert_json_schema(response: Response, schema: type[BaseModel]) -> None:
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


    @staticmethod
    @allure.step("Check XML tag present: {expected_tag}")
    def assert_xml_tag_present(response: Response, expected_tag: str) -> None:
        """
        Проверяет наличие указанного тега в XML-теле ответа.
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

        if root.tag != expected_tag and not root.findall(f".//{expected_tag}"):
            allure.attach(
                response.text,
                name="XML Body",
                attachment_type=allure.attachment_type.XML
            )
            raise AssertionError(f"XML tag '{expected_tag}' not found in response")