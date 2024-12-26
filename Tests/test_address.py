import pytest
from fastapi.testclient import TestClient

from Models.response import BaseResponse
from Models.user import AddressBase, User, UserAddress


@pytest.fixture(scope="session", autouse=True)
def address(authorized_client: TestClient):
    response = authorized_client.post(
        "/user/address",
        json=AddressBase(name="A1", phone="1234567890", address="Foo").model_dump(),
        params={"is_default": True},
    )

    assert response.status_code == 201
    aid = BaseResponse[str].model_validate(response.json()).data
    assert aid is not None
    return aid


def test_add_address(authorized_client: TestClient):
    response = authorized_client.post(
        "/user/address",
        json=AddressBase(name="A2", phone="1234567890", address="Bar").model_dump(),
        params={"is_default": True},
    )

    assert response.status_code == 201
    aid = BaseResponse[str].model_validate(response.json()).data
    assert aid is not None

    response = authorized_client.get("/user/address")

    assert response.status_code == 200
    data = BaseResponse[list[UserAddress]].model_validate(response.json()).data
    assert data is not None
    assert len(data) == 2

    response = authorized_client.get("/user/profile")
    data = BaseResponse[User].model_validate(response.json()).data
    assert data is not None and data.aid == aid


@pytest.mark.order(after="test_add_address")
def test_edit_address(authorized_client: TestClient, address: str):
    response = authorized_client.put(
        f"/user/address/{address}",
        json=AddressBase(name="A3", phone="1234567890", address="Banana").model_dump(),
        params={"is_default": False},
    )

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get("/user/address")
    data = BaseResponse[list[UserAddress]].model_validate(response.json()).data
    assert data is not None
    assert [item for item in data if item.aid == address][0].address == "Banana"

    response = authorized_client.put(
        f"/user/address/{address}",
        json=AddressBase(name="A4", phone="1234567890", address="DX").model_dump(),
        params={"is_default": True},
    )

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get("/user/address")
    data = BaseResponse[list[UserAddress]].model_validate(response.json()).data
    assert data is not None

    response = authorized_client.get("/user/profile")
    data = BaseResponse[User].model_validate(response.json()).data
    assert data is not None and data.aid == address

    response = authorized_client.get(f"/user/address/{data.aid}")
    data = BaseResponse[UserAddress].model_validate(response.json()).data
    assert data is not None and data.address == "DX"


@pytest.mark.order(after="test_edit_address")
def test_delete_address(authorized_client: TestClient, address: str):
    response = authorized_client.delete(f"/user/address/{address}")

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get("/user/address")
    data = BaseResponse[list[UserAddress]].model_validate(response.json()).data
    assert data is not None
    assert len(data) == 1

    response = authorized_client.get("/user/profile")
    data = BaseResponse[User].model_validate(response.json()).data
    assert data is not None and data.aid is None
