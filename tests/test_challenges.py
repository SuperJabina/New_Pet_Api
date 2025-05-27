import pytest
import allure
from http import HTTPStatus
from clients.challenges_client import ChallengesClient
from clients.todos_client import TodosClient
from tools.assertions.schema.challenges_model import ChallengesSchema
from tools.assertions.schema.todos_model import TodosSchema
from tools.assertions.challenges_assertions import ChallengesAsserts
from tools.assertions.todos_assertions import TodosAsserts
from tools.assertions.schema.xsd_paths import XSDPaths

@pytest.mark.challenges
@allure.feature("Challenges API")
class TestChallenges(ChallengesAsserts):

    @pytest.mark.regression
    @allure.title("Get new challenger token")
    def test_01_get_new_challenger(self, challenges_client):
        response = challenges_client.generate_new_challenger()
        self.assert_status_code(response, 201)
        self.assert_response_time(response, max_time=5.0)
        self.assert_headers_present(response, ["X-CHALLENGER", "Location"])

    @pytest.mark.regression
    @allure.title("Get all challenges. Using extra headers[{headers}]")
    @pytest.mark.parametrize(
        "headers, expected_status",
        [
            (None, HTTPStatus.OK),  # Заголовки по умолчанию (из settings)
            ({"X-Challenger": ""}, HTTPStatus.OK),  # Пустой X-Challenger
            ({"X-Challenger": "test_token", "Accept": "application/xml"}, HTTPStatus.OK),  # Дополнительный заголовок
            ({"Authorization": "Bearer invalid"}, HTTPStatus.OK),  # Неверный заголовок
        ],
        ids=[
            "default_headers",
            "empty_token",
            "Accept_with_application/xml",
            "invalid_authorization"
        ]
    )
    def test_02_get_challenges(self, challenges_client: ChallengesClient, headers: dict | None, expected_status: int):
        """
        Тестирует GET /challenges с различными заголовками.
        """
        checks = {
            "status_code" : expected_status,
            "response_time" : 5.0,
            "schema" : True,
            "headers_present" : ["content-type"],
            "header_values" : None,
            "key_present" : ["challenges"],
            "key_value" : {"id": 59},
            "request_headers": headers
        }
        response = challenges_client.get_challenges_api(headers=headers)
        self.comprehensive_checks(response=response, checks=checks)

@allure.feature("/todos API")
class TestTodos(TodosAsserts):

    @pytest.mark.regression
    @allure.title("Get all todos. Using extra headers[{headers}]")
    @pytest.mark.parametrize(
        "headers, expected_status",
        [
            (None, HTTPStatus.OK),  # Заголовки по умолчанию (из settings)
            ({"X-Challenger": ""}, HTTPStatus.OK),  # Пустой X-Challenger
            ({"X-Challenger": "test_token", "Accept": "application/xml"}, HTTPStatus.OK),  # Дополнительный заголовок
            ({"Authorization": "Bearer invalid"}, HTTPStatus.OK),  # Неверный заголовок
        ],
        ids=[
            "default_headers",
            "empty_token",
            "Accept_with_application/xml",
            "invalid_authorization"
        ]
    )
    def test_03_get_all_todos(self, todos_client: TodosClient, headers: dict | None, expected_status: int):
        """
        Тестирует GET /todos с различными заголовками.
        """
        checks = {
            "status_code" : expected_status,
            "response_time" : 5.0,
            "schema" : True,
            "headers_present" : ["content-type"],
            "header_values" : None,
            "key_present" : ["todos"],
            "key_value" : {"id": 7},
            "request_headers": headers
        }
        response = todos_client.get_all_todos(headers=headers)
        self.comprehensive_checks(response=response, checks=checks)


