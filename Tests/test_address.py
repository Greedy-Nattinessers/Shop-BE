import pytest
from fastapi.testclient import TestClient

from Models.response import BaseResponse
from Models.user import AddressBase, UserAddress


@pytest.fixture(scope="session")
def address(authorized_client: TestClient):
    response = authorized_client.post(
        "/user/address",
        json=AddressBase(
            name="A1", phone="1234567890", address="Foo", is_default=True
        ).model_dump(),
    )

    assert response.status_code == 201
    aid = BaseResponse[str].model_validate(response.json()).data
    assert aid is not None
    return aid


def test_add_address(authorized_client: TestClient):
    response = authorized_client.post(
        "/user/address",
        json=AddressBase(
            name="A2", phone="1234567890", address="Bar", is_default=True
        ).model_dump(),
    )

    assert response.status_code == 201
    aid = BaseResponse[str].model_validate(response.json()).data
    assert aid is not None

    response = authorized_client.get("/user/address")

    assert response.status_code == 200
    data = BaseResponse[list[UserAddress]].model_validate(response.json()).data
    assert data is not None
    default_list = [item for item in data if item.is_default]
    assert len(default_list) == 1 and default_list[0].name == "A2"


@pytest.mark.order(after="test_add_address")
def test_edit_address(authorized_client: TestClient, address: str):
    response = authorized_client.put(
        f"/user/address/{address}",
        json=AddressBase(
            name="A3", phone="1234567890", address="Banana", is_default=False
        ).model_dump(),
    )

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get("/user/address")
    data = BaseResponse[list[UserAddress]].model_validate(response.json()).data
    assert data is not None
    assert [item for item in data if item.aid == address][0].address == "Banana"

    response = authorized_client.put(
        f"/user/address/{address}",
        json=AddressBase(
            name="A4", phone="1234567890", address="DX", is_default=True
        ).model_dump(),
    )

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get("/user/address")
    data = BaseResponse[list[UserAddress]].model_validate(response.json()).data
    assert data is not None
    default_list = [item for item in data if item.is_default]
    assert len(default_list) == 1 and default_list[0].name == "A4"


@pytest.mark.order(after="test_edit_address")
def test_delete_address(authorized_client: TestClient, address: str):
    response = authorized_client.delete(f"/user/address/{address}")

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get("/user/address")
    data = BaseResponse[list[UserAddress]].model_validate(response.json()).data
    assert data is not None
    assert len(data) == 1
