from typing import Dict, Any

from httpx import Response
from pydantic import BaseModel, ValidationError
from tools.assertions.base_assertions import BaseResponseAsserts
import allure
import json
import xml.etree.ElementTree as ET

from tools.assertions.schema.challenges_model import ChallengesSchema
from tools.assertions.schema.xsd_paths import XSDPaths


class ChallengesAsserts(BaseResponseAsserts):
    """
    Класс для расширенных проверок "/challenges".
    Наследуется от BaseResponseAsserts.
    """

    schema = ChallengesSchema
    xsd_path = XSDPaths.CHALLENGES_XSD.path






