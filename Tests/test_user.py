import datetime
import secrets
from time import sleep

from fastapi.testclient import TestClient

from Models.response import BaseResponse
from Models.user import Token
from Services.Config.config import config, InvalidConfigError
from main import app
from Services.Mail.mail import Purpose
from Tests.Utils.user import get_captcha

client = TestClient(app)


if (test_config := config.test) is None:
    raise InvalidConfigError("Test environment not enabled")

secure_rng = secrets.SystemRandom()
test_username = f"BotDuang-{secure_rng.randint(1000, 9999)}"
test_password = secrets.token_urlsafe(16)
valid_user = False
access_token: str | None = None


def test_user_register():
    assert test_config is not None

    captcha_response = client.get(
        "/user/captcha",
        params={"email": test_config.email.address, "purpose": Purpose.REGISTER.value},
    )

    assert captcha_response.status_code == 200
    assert captcha_response.json()["status_code"] == 200
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
    )

    assert register_response.status_code == 201
    BaseResponse[None].model_validate(register_response.json())
    global valid_user
    valid_user = True


def test_user_login():
    login_response = client.post(
        "/user/login",
        data={"username": test_username, "password": test_password},
    )

    if not valid_user:
        print("[!] User not registered, using unauthorized login test")
        assert login_response.status_code == 401
        return
    
    assert login_response.status_code == 200
    data = BaseResponse[Token].model_validate(login_response.json())
    assert data.data is not None
    global access_token
    access_token = data.data.access_token
