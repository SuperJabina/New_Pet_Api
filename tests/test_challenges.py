import random

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
class TestChallenges:
    @allure.story("Getting Started")
    class TestGettingStarted(ChallengesAsserts):

        @pytest.mark.skip
        @pytest.mark.regression
        @allure.title("Get new challenger token")
        def test_01_get_new_challenger(self, challenges_client):
            response = challenges_client.generate_new_challenger()
            self.assert_status_code(response, 201)
            self.assert_response_time(response, max_time=5.0)
            self.assert_headers_present(response, ["X-CHALLENGER", "Location"])

    @allure.story("First Real Challenge")
    class TestFirstRealChallenge(ChallengesAsserts):

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
                "status_code": expected_status,
                "response_time": 5.0,
                "schema": True,
                "headers_present": ["content-type"],
                "header_values": None,
                "key_present": ["challenges"],
                "key_value": {"id": 59},
                "request_headers": headers
            }
            response = challenges_client.get_challenges_api(headers=headers)
            self.comprehensive_checks(response=response, checks=checks)


    @allure.story("Get Challenges")
    class TestGetChallenges(TodosAsserts):

        @pytest.mark.regression
        @allure.title("Get all todos. Headers[{headers}] Params [{params}]")
        @pytest.mark.parametrize(
            "headers, params, expected_status",
            [
                (None, None, HTTPStatus.OK),  # Заголовки по умолчанию (из settings)
                (None, {"doneStatus": True},HTTPStatus.OK),  # query параметр/фильтр
                ({"X-Challenger": ""},None, HTTPStatus.OK),  # Пустой X-Challenger
                ({"X-Challenger": "test_token", "Accept": "application/xml"}, None, HTTPStatus.OK),  # Дополнительный
                # заголовок
                (None, {"id": 3}, HTTPStatus.OK),  # query параметр/фильтр
                ({"Authorization": "Bearer invalid"}, None, HTTPStatus.OK),  # Неверный заголовок
            ],
            ids=[
                "default_headers",
                "doneStatus: True",
                "empty_token",
                "Accept_with_application/xml",
                "id: 3",
                "Wrong token"
            ]
        )
        def test_03_get_all_todos(self, todos_client: TodosClient, headers: dict | None, params: dict |
                                                                                                 None, expected_status:
        int):
            """
            Тестирует GET /todos с различными заголовками.
            """
            checks = {
                "status_code": expected_status,
                "response_time": 5.0,
                "schema": True,
                "headers_present": ["content-type"],
                "header_values": None,
                "key_present": ["todos"],
                "key_value": params,
                "request_headers": headers
            }
            response = todos_client.get_all_todos(headers=headers, params=params)
            self.comprehensive_checks(response=response, checks=checks)
            if params:
                self.check_query_filter(response=response, params=params)

        @pytest.mark.extension
        @allure.title("GET request on the incorrect '/todo' endpoint")
        def test_04_get_todo_404(self, todos_client: TodosClient):
            """
            Тестирует GET /todo (неправильный эндпоинт).
            """
            response = todos_client.get("/todo")
            self.assert_status_code(response, 404)

        @pytest.mark.regression
        @allure.title("GET todo with ID [{todo_id}] (None for random)")
        @pytest.mark.parametrize(
            "todo_id, headers, expected_status",
            [
                (None, None, HTTPStatus.OK),  # случайный ID, Заголовки по умолчанию (из settings)
                (5, {"X-Challenger": ""}, HTTPStatus.OK),  # Определенный ID со статусом True
                (150, None, HTTPStatus.NOT_FOUND),
                # несуществующий ID
                (None, {"Accept": "application/xml"}, HTTPStatus.OK) # ответ в XML
            ],
            ids=[
                "random ID",
                "specific ID",
                "Wrong ID",
                "Random ID XML"
            ]
        )
        def test_05_get_specific_todo(self, todos_client: TodosClient, todo_id: int, headers: dict | None, expected_status:
        int):
            """
            Тестирует GET /todos{id} с различными заголовками.
            """
            checks = {
                "status_code": expected_status,
                "response_time": 5.0,
                "schema": True,
                "headers_present": ["content-type"],
                "header_values": None,
                "key_present": ["todos"],
                "key_value": {"id": todo_id},
                "request_headers": headers
            }
            if todo_id is None:
                available_ids = todos_client.get_available_ids()
                todo_id = random.choice(available_ids)
                checks["key_value"] = {"id": todo_id}
                allure.attach(str(id), name="Random ID", attachment_type=allure.attachment_type.TEXT)

            response = todos_client.get_specific_todo(todo_id=todo_id, headers=headers)
            self.comprehensive_checks(response=response, checks=checks)

    @allure.story("HEAD Challenges")
    class TestHeadChallenges(TodosAsserts):
        @pytest.mark.regression
        @allure.title("HEAD request /todos")
        def test_head_request_todos(self, todos_client: TodosClient):
            response = todos_client.head(url="/todos")
            self.assert_status_code(response=response, expected_status=200)
            self.assert_headers_present(response=response, expected_headers=["X-CHALLENGER"])


