from datetime import datetime
import secrets
from time import sleep

from fastapi.encoders import jsonable_encoder
import pytest
from fastapi.testclient import TestClient

from Models.response import BaseResponse
from Models.user import Gender, Permission, Token, User
from Services.Config.config import InvalidConfigError, config
from Tests.Utils.user import get_captcha


def test_user_profile(authorized_client: TestClient):
    profile_response = authorized_client.get("/user/profile")

    assert profile_response.status_code == 200
    data = BaseResponse[User].model_validate(profile_response.json()).data
    assert (
        data is not None
        and data.permission == Permission.ADMIN
        and data.gender == Gender.MALE.value
    )


def test_user_recover(authorized_client: TestClient):
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
    username = BaseResponse[str].model_validate(recover_response.json()).data
    assert username is not None

    login_response = authorized_client.post(
        "/user/login",
        data={"username": username, "password": test_password},
    )

    assert login_response.status_code == 200
    token = BaseResponse[Token].model_validate(login_response.json()).data
    assert token is not None
    authorized_client.headers.update({"Authorization": f"Bearer {token.access_token}"})


@pytest.mark.order("last")
def test_user_update(authorized_client: TestClient, register_user: tuple[str, str]):
    profile_response = authorized_client.get("/user/profile")

    assert profile_response.status_code == 200
    data = BaseResponse[User].model_validate(profile_response.json()).data
    assert data is not None
    user_id = data.uid

    new_password = secrets.token_urlsafe(16)
    date = datetime.now().date()
    update_response = authorized_client.put(
        f"/user/profile/{user_id}",
        json=jsonable_encoder(
            {
                "gender": Gender.FEMALE.value,
                "birthday": date.strftime("%Y-%m-%d"),
                "password": new_password,
                "permission": Permission.USER(),
            }
        ),
    )

    assert update_response.status_code == 200
    BaseResponse[None].model_validate(update_response.json())

    login_response = authorized_client.post(
        "/user/login",
        data={"username": register_user[0], "password": new_password},
    )

    assert login_response.status_code == 200
    token = BaseResponse[Token].model_validate(login_response.json()).data
    assert token is not None

    authorized_client.headers.update({"Authorization": f"Bearer {token.access_token}"})

    profile_response = authorized_client.get("/user/profile")
    assert profile_response.status_code == 200
    assert (
        (data := BaseResponse[User].model_validate(profile_response.json()).data)
        and data.permission == Permission.USER
        and data.birthday == date
        and data.gender == Gender.FEMALE
    )
