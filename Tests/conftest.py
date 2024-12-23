import secrets
from time import sleep

import pytest
from fastapi.testclient import TestClient

from main import app
from Models.response import BaseResponse
from Models.user import Gender, Token
from Services.Config.config import InvalidConfigError, config
from Tests.Utils.user import get_captcha

if (test_config := config.test) is None or not test_config.is_test:
    raise InvalidConfigError("Test environment not enabled")


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def register_user(client: TestClient) -> tuple[str, str]:
    assert test_config is not None
    secure_rng = secrets.SystemRandom()
    test_username = f"BotDuang-{secure_rng.randint(1000, 9999)}"
    test_password = secrets.token_urlsafe(16)

    captcha_response = client.get(
        "/user/captcha/register", params={"email": test_config.email.address}
    )

    assert captcha_response.status_code == 200
    assert (
        request_id := BaseResponse[str].model_validate(captcha_response.json()).data
    ) is not None
    sleep(5)

    captcha = get_captcha(**test_config.email.model_dump())

    assert isinstance(captcha, str)
    register_response = client.post(
        "/user/register",
        data={
            "username": test_username,
            "password": test_password,
            "email": test_config.email.address,
            "gender": str(Gender.MALE.value),
            "captcha": captcha,
        },
        headers={"request-id": request_id},
    )

    assert register_response.status_code == 201
    BaseResponse[None].model_validate(register_response.json())

    return test_username, test_password


@pytest.fixture(scope="session")
def login_user(client: TestClient, register_user: tuple[str, str]) -> str:
    test_username, test_password = register_user
    login_response = client.post(
        "/user/login",
        data={"username": test_username, "password": test_password},
    )

    assert login_response.status_code == 200
    data = BaseResponse[Token].model_validate(login_response.json()).data
    assert data is not None
    access_token = data.access_token

    return access_token


@pytest.fixture(scope="session")
def authorized_client(client: TestClient, login_user: str) -> TestClient:
    client.headers.update({"Authorization": f"Bearer {login_user}"})
    return client
