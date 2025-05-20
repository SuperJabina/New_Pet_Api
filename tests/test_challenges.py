import pytest
import allure
from http import HTTPStatus
from clients.challenges_client import ChallengesClient
from schema.challenges import ChallengesSchema
from tools.assertions.challenges_assertions import ChallengesAsserts

@pytest.mark.challenges
@allure.feature("Challenges API")
class TestChallenges:
    @pytest.mark.regression
    @allure.title("Get all challenges with headers={headers}")
    @pytest.mark.parametrize(
        "headers, expected_status",
        [
            (None, HTTPStatus.UNAUTHORIZED),  # Заголовки по умолчанию (из settings)
            ({"X-Challenger": ""}, HTTPStatus.OK),  # Пустой X-Challenger
            ({"X-Challenger": "test_token", "Accept": "application/xml"}, HTTPStatus.UNAUTHORIZED),  # Дополнительный заголовок
            ({"Authorization": "Bearer invalid"}, HTTPStatus.OK),  # Неверный заголовок
        ],
        ids=[
            "default_headers",
            "empty_headers",
            "Accept_with_application/xml",
            "invalid_authorization"
        ]
    )
    def test_get_challenges(self, challenges_client: ChallengesClient, headers: dict | None, expected_status: int):
        """
        Тестирует GET /challenges с различными заголовками.
        """
        response = challenges_client.get_challenges_api(headers=headers)

        ChallengesAsserts.assert_status_code(response, expected_status)
        ChallengesAsserts.assert_response_time(response, max_time=5.0)
        ChallengesAsserts.assert_headers_present(response, ["content-type"])

        if expected_status == HTTPStatus.OK:
            is_xml = headers is not None and headers.get("Accept") == "application/xml"
            if is_xml:
                ChallengesAsserts.assert_header_values(response, {"content-type": "application/xml"})
                ChallengesAsserts.assert_xml_tag_present(response, "challenges")
            else:
                ChallengesAsserts.assert_body_keys_present(response, ["challenges"])
                ChallengesAsserts.assert_header_values(response, {"content-type": "application/json"})
                ChallengesAsserts.assert_json_schema(response, ChallengesSchema)


