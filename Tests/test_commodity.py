import hashlib

import pytest
from fastapi.testclient import TestClient

from Models.commodity import BaseCommodity, Comment, Commodity, CreateCommodity
from Models.response import BaseResponse


@pytest.fixture(scope="session")
def create_commodity(authorized_client: TestClient):
    images = []
    for file in ["Tests/Resources/commodity.jpg", "Tests/Resources/commodity_2.png"]:
        with open(file, "rb") as f:
            images.append(("images", (f.name, f.read(), "image/jpeg")))

    response = authorized_client.post(
        "/shop/add",
        data={
            "body": CreateCommodity(
                name="TestCommodity", price=100, description="Test"
            ).model_dump_json(),
        },
        files=images,
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


def test_get_commodity(client: TestClient, create_commodity: str):
    commodity_response = client.get(f"/shop/item/{create_commodity}")

    assert commodity_response.status_code == 200
    data = BaseResponse[Commodity].model_validate(commodity_response.json()).data
    assert data is not None and data.description == "Test"

    album_response = client.get(f"/shop/item/{create_commodity}/album")
    assert album_response.status_code == 200

    image_response = client.get(f"/shop/image/{data.images[1]}")
    assert image_response.status_code == 200

    with open("Tests/Resources/commodity.jpg", "rb") as f:
        assert (
            hashlib.sha256(album_response.content).hexdigest()
            == hashlib.sha256(f.read()).hexdigest()
        )
    with open("Tests/Resources/commodity_2.png", "rb") as f:
        assert (
            hashlib.sha256(image_response.content).hexdigest()
            == hashlib.sha256(f.read()).hexdigest()
        )


def test_comment(authorized_client: TestClient, create_commodity: str):
    add_response = authorized_client.post(
        f"/shop/item/{create_commodity}/comment",
        json={"content": "TestComment"},
    )

    assert add_response.status_code == 201
    BaseResponse[None].model_validate(add_response.json())

    get_response = authorized_client.get(f"/shop/item/{create_commodity}/comment")
    assert get_response.status_code == 200
    data = BaseResponse[list[Comment]].model_validate(get_response.json()).data
    assert data is not None and len(data) == 1
    assert data[0].content == "TestComment"
    cid = data[0].cid

    del_response = authorized_client.delete(f"/shop/comment/{cid}")
    assert del_response.status_code == 200
    BaseResponse[None].model_validate(del_response.json())

    get_response = authorized_client.get(f"/shop/item/{create_commodity}/comment")
    assert get_response.status_code == 200
    data = BaseResponse[list[Comment]].model_validate(get_response.json()).data
    assert data is not None and len(data) == 0

    response = authorized_client.post(
        f"/shop/item/{create_commodity}/comment", json={"content": "Leave Comment"}
    )
    assert response.status_code == 201
    BaseResponse[None].model_validate(response.json())


@pytest.mark.order(after="test_get_commodity")
def test_commodity_edit(authorized_client: TestClient, create_commodity: str):
    with open("Tests/Resources/commodity_2.png", "rb") as f:
        data = f.read()
        response = authorized_client.put(
            f"/shop/item/{create_commodity}",
            data={"body": '{"price": 200}'},
            files={"images": (f.name, data, "image/png")},
        )
        sha = hashlib.sha256(data).hexdigest()

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get(f"/shop/item/{create_commodity}")
    assert response.status_code == 200
    data = BaseResponse[Commodity].model_validate(response.json()).data
    assert data is not None
    assert data.price == 200
    assert len(data.images) == 1

    album_response = authorized_client.get(f"/shop/image/{data.album}")
    assert album_response.status_code == 200
    assert hashlib.sha256(album_response.content).hexdigest() == sha


@pytest.mark.order(after="test_commodity_edit")
def test_commodity_delete(authorized_client: TestClient, create_commodity: str):
    response = authorized_client.delete(
        f"/shop/item/{create_commodity}",
    )

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())

    response = authorized_client.get(f"/shop/item/{create_commodity}")
    assert response.status_code == 404
    BaseResponse[None].model_validate(response.json())
