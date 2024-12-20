import pytest
from fastapi.testclient import TestClient

from Models.commodity import CartCommodity, CreateCommodity
from Models.response import BaseResponse


@pytest.fixture(scope="session")
def cart_commodity_a(authorized_client: TestClient):
    response = authorized_client.post(
        "/shop/add",
        data={
            "body": CreateCommodity(
                name="TestCommodity", price=100, description="Test"
            ).model_dump_json(),
        },
    )

    assert response.status_code == 201
    cid = BaseResponse[str].model_validate(response.json()).data
    assert cid is not None
    return cid


@pytest.fixture(scope="session")
def cart_commodity_b(authorized_client: TestClient):
    response = authorized_client.post(
        "/shop/add",
        data={
            "body": CreateCommodity(
                name="TestCommodity", price=100, description="Test"
            ).model_dump_json(),
        },
    )

    assert response.status_code == 201
    cid = BaseResponse[str].model_validate(response.json()).data
    assert cid is not None
    return cid


def test_add_cart(authorized_client: TestClient, cart_commodity_a: str):
    add_response = authorized_client.post(f"/cart/add/{cart_commodity_a}")

    assert add_response.status_code == 200
    BaseResponse[None].model_validate(add_response.json())

    get_response = authorized_client.get("/cart/all")

    assert get_response.status_code == 200
    data = BaseResponse[list[CartCommodity]].model_validate(get_response.json()).data
    assert data is not None and data[0].cid == cart_commodity_a and data[0].count == 1

    add_response = authorized_client.post(f"/cart/add/{cart_commodity_a}")

    assert add_response.status_code == 200
    BaseResponse[None].model_validate(add_response.json())

    get_response = authorized_client.get("/cart/all")

    assert get_response.status_code == 200
    data = BaseResponse[list[CartCommodity]].model_validate(get_response.json()).data
    assert data is not None and data[0].cid == cart_commodity_a and data[0].count == 2


@pytest.mark.order(after="test_add_cart")
def test_reduce_cart(authorized_client: TestClient, cart_commodity_a: str):
    del_response = authorized_client.delete(f"/cart/remove/{cart_commodity_a}")

    assert del_response.status_code == 200
    BaseResponse[None].model_validate(del_response.json())

    get_response = authorized_client.get("/cart/all")

    assert get_response.status_code == 200
    data = BaseResponse[list[CartCommodity]].model_validate(get_response.json()).data
    assert data is not None and data[0].cid == cart_commodity_a and data[0].count == 1

    del_response = authorized_client.delete(f"/cart/remove/{cart_commodity_a}")

    assert del_response.status_code == 200
    BaseResponse[None].model_validate(del_response.json())

    get_response = authorized_client.get("/cart/all")

    assert get_response.status_code == 200
    data = BaseResponse[list[CartCommodity]].model_validate(get_response.json()).data
    assert data is not None and len(data) == 0

    # recover prev env
    test_add_cart(authorized_client, cart_commodity_a)
    del_response = authorized_client.delete(
        f"/cart/remove/{cart_commodity_a}", params={"remove_all": True}
    )

    assert del_response.status_code == 200
    BaseResponse[None].model_validate(del_response.json())

    get_response = authorized_client.get("/cart/all")

    assert get_response.status_code == 200
    data = BaseResponse[list[CartCommodity]].model_validate(get_response.json()).data
    assert data is not None and len(data) == 0


@pytest.mark.order(after="test_reduce_cart")
def test_clear_cart(
    authorized_client: TestClient, cart_commodity_a: str, cart_commodity_b: str
):
    test_add_cart(authorized_client, cart_commodity_a)
    add_response = authorized_client.post(f"/cart/add/{cart_commodity_b}")

    assert add_response.status_code == 200
    BaseResponse[None].model_validate(add_response.json())

    get_response = authorized_client.get("/cart/all")

    assert get_response.status_code == 200
    data = BaseResponse[list[CartCommodity]].model_validate(get_response.json()).data
    assert data is not None and len(data) == 2

    del_response = authorized_client.delete("/cart/all")

    assert del_response.status_code == 200
    BaseResponse[None].model_validate(del_response.json())

    get_response = authorized_client.get("/cart/all")

    assert get_response.status_code == 200
    data = BaseResponse[list[CartCommodity]].model_validate(get_response.json()).data
    assert data is not None and len(data) == 0
