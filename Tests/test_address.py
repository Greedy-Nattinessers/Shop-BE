import pytest
from fastapi.testclient import TestClient

from Models.response import BaseResponse
from Models.user import AddressRequest, UserAddress


@pytest.mark.parametrize(
    "address",
    [
        AddressRequest(name="A1", phone="1234567890", address="Foo", is_default=True),
        AddressRequest(name="A2", phone="0987654321", address="Bar", is_default=True),
    ],
)
def test_create_address(authorized_client: TestClient, address: AddressRequest):
    response = authorized_client.post(
        "/user/address",
        json=address.model_dump(),
    )

    assert response.status_code == 201
    BaseResponse[None].model_validate(response.json())


def test_all_address(authorized_client: TestClient):
    response = authorized_client.get("/user/address")

    assert response.status_code == 200
    data = BaseResponse[list[UserAddress]].model_validate(response.json()).data
    assert data is not None
    default_list = [item for item in data if item.is_default]
    assert len(default_list) == 1 and default_list[0].name == "A2"

def test_delete_address(authorized_client: TestClient):
    get_response = authorized_client.get("/user/address")

    assert get_response.status_code == 200
    data = BaseResponse[list[UserAddress]].model_validate(get_response.json()).data
    assert data is not None

    aid = data[0].aid
    response = authorized_client.delete(f"/user/address/{aid}")

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())