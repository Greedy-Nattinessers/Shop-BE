import secrets
from time import sleep

import pytest
from fastapi.testclient import TestClient

from main import app
from Models.response import BaseResponse
from Models.user import Token, User
from Services.Config.config import InvalidConfigError, config
from Tests.Utils.user import get_captcha

client = TestClient(app)


if (test_config := config.test) is None:
    raise InvalidConfigError("Test environment not enabled")

secure_rng = secrets.SystemRandom()
test_username = f"BotDuang-{secure_rng.randint(1000, 9999)}"
test_password = secrets.token_urlsafe(16)
access_token: str | None = None

@pytest.mark.order(1)
def test_user_register():
    assert test_config is not None

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
            "captcha": captcha,
        },
        headers={"request-id": request_id},
    )

    assert register_response.status_code == 201
    BaseResponse[None].model_validate(register_response.json())


@pytest.mark.parametrize(
    "username, password, is_valid",
    [(test_username, test_password, True), ("foo", "bar", False)],
)
@pytest.mark.order(after="test_user_register")
def test_user_login(username: str, password: str, is_valid: bool):
    login_response = client.post(
        "/user/login",
        data={"username": username, "password": password},
    )

    if not is_valid:
        print("[!] User not registered, using unauthorized login test")
        assert login_response.status_code == 401
        return

    assert login_response.status_code == 200
    data = BaseResponse[Token].model_validate(login_response.json())
    assert data.data is not None
    global access_token
    access_token = data.data.access_token


@pytest.mark.order(after="test_user_login")
def test_user_profile():
    assert access_token is not None

    profile_response = client.get(
        "/user/profile", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert profile_response.status_code == 200
    data = BaseResponse[User].model_validate(profile_response.json())
    assert data.data is not None
    assert data.data.username == test_username


@pytest.mark.order(after="test_user_profile")
def test_user_recover():
    assert test_config is not None

    captcha_response = client.get(
        "/user/captcha/recover", params={"email": test_config.email.address}
    )

    assert captcha_response.status_code == 200
    assert (
        request_id := BaseResponse[str].model_validate(captcha_response.json()).data
    ) is not None
    sleep(5)

    captcha = get_captcha(**test_config.email.model_dump())
    assert isinstance(captcha, str)

    global test_password
    test_password = secrets.token_urlsafe(16)
    recover_response = client.post(
        "/user/recover",
        data={
            "email": test_config.email.address,
            "password": test_password,
            "captcha": captcha,
        },
        headers={"request-id": request_id},
    )

    assert recover_response.status_code == 200
    BaseResponse[None].model_validate(recover_response.json())

    test_user_login(test_username, test_password, True)
