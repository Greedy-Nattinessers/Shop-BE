import pytest
from fastapi.testclient import TestClient

from Models.commodity import BaseCommodity, Commodity, CreateCommodity
from Models.response import BaseResponse


@pytest.fixture(scope="session")
def create_commodity(authorized_client: TestClient):
    with open("Tests/Resources/commodity.jpg", "rb") as f:
        img = f.read()
        response = authorized_client.post(
            "/shop/add",
            data={
                "body": CreateCommodity(
                    name="TestCommodity", price=100, description="Test"
                ).model_dump_json(),
            },
            files={"images": ("commodity.jpg", img, "image/jpeg")},
        )

        assert response.status_code == 201
        cid = BaseResponse[str].model_validate(response.json()).data
        assert cid is not None
        return cid


def test_commodity_all(client: TestClient, create_commodity: str):
    response = client.get("/shop/all")

    assert response.status_code == 200
    data = BaseResponse[list[BaseCommodity]].model_validate(response.json()).data
    assert data is not None and len(data) > 0
    assert create_commodity in [item.cid for item in data]


def test_commodity_edit(authorized_client: TestClient, create_commodity: str):
    response = authorized_client.put(
        f"/shop/item/{create_commodity}",
        data={"body": '{"price": 200}'},
    )

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get(f"/shop/item/{create_commodity}")
    assert response.status_code == 200
    data = BaseResponse[Commodity].model_validate(response.json()).data
    assert data is not None
    assert data.price == 200


@pytest.mark.order(after="test_commodity_edit")
def test_commodity_delete(authorized_client: TestClient, create_commodity: str):
    response = authorized_client.delete(
        f"/shop/delete/{create_commodity}",
    )

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get(f"/shop/item/{create_commodity}")
    assert response.status_code == 404
    BaseResponse[None].model_validate(response.json())
