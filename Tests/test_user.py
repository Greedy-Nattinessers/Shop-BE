import secrets
from time import sleep

from fastapi.testclient import TestClient

from Models.response import BaseResponse
from Models.user import Token, User
from Services.Config.config import InvalidConfigError, config
from Tests.Utils.user import get_captcha


def test_user_profile(authorized_client: TestClient):

    profile_response = authorized_client.get("/user/profile")

    assert profile_response.status_code == 200
    assert BaseResponse[User].model_validate(profile_response.json()) is not None


def test_user_recover(authorized_client: TestClient, register_user: tuple[str, str]):
    if (test_config := config.test) is None:
        raise InvalidConfigError("Test environment not enabled")

    captcha_response = authorized_client.get(
        "/user/captcha/recover", params={"email": test_config.email.address}
    )

    assert captcha_response.status_code == 200
    assert (
        request_id := BaseResponse[str].model_validate(captcha_response.json()).data
    ) is not None
    sleep(5)

    captcha = get_captcha(**test_config.email.model_dump())
    assert isinstance(captcha, str)

    test_password = secrets.token_urlsafe(16)
    recover_response = authorized_client.post(
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

    login_response = authorized_client.post(
        "/user/login",
        data={"username": register_user[0], "password": test_password},
    )

    assert login_response.status_code == 200
    token = BaseResponse[Token].model_validate(login_response.json()).data
    assert token is not None
    authorized_client.headers.update({"Authorization": f"Bearer {token}"})
