from httpx import Response
from pydantic import BaseModel, ValidationError
from tools.assertions.base_assertions import BaseResponseAsserts
from tools.assertions.schema.todos_model import TodosSchema
from tools.assertions.schema.xsd_paths import XSDPaths
import allure
import json
import xml.etree.ElementTree as ET


class TodosAsserts(BaseResponseAsserts):
    """
    Класс для расширенных проверок "/challenges".
    Наследуется от BaseResponseAsserts.
    """

    schema = TodosSchema
    xsd_path = XSDPaths.TODOS_XSD.path