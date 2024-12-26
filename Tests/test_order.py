import pytest
from fastapi.testclient import TestClient

from Models.commodity import CreateCommodity
from Models.order import Order, OrderBase, OrderStatus
from Models.response import BaseResponse
from Models.user import AddressBase


@pytest.fixture(scope="session")
def order_commodity(authorized_client: TestClient):
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
def address(authorized_client: TestClient):
    response = authorized_client.post(
        "/user/address",
        json=AddressBase(name="O1", phone="1234567890", address="Order").model_dump(),
        params={"is_default": False},
    )

    assert response.status_code == 201
    aid = BaseResponse[str].model_validate(response.json()).data
    assert aid is not None
    return aid


@pytest.fixture(scope="session", autouse=True)
def order_commodity_a(
    authorized_client: TestClient, address: str, order_commodity: str
):
    response = authorized_client.post(
        "/order/add",
        json=OrderBase(aid=address, content={order_commodity: 5}).model_dump(),
    )

    assert response.status_code == 201
    oid = BaseResponse[str].model_validate(response.json()).data
    assert oid is not None
    return oid


@pytest.fixture(scope="session", autouse=True)
def order_commodity_b(
    authorized_client: TestClient, address: str, order_commodity: str
):
    response = authorized_client.post(
        "/order/add",
        json=OrderBase(aid=address, content={order_commodity: 3}).model_dump(),
    )

    assert response.status_code == 201
    oid = BaseResponse[str].model_validate(response.json()).data
    assert oid is not None
    return oid


def test_all_order(authorized_client: TestClient):
    response = authorized_client.get("/order/list")

    assert response.status_code == 200
    data = BaseResponse[list[Order]].model_validate(response.json()).data
    assert data is not None and len(data) == 2


@pytest.mark.order(after="test_all_order")
def test_cancel_order(authorized_client: TestClient, order_commodity_a: str):
    response = authorized_client.put(f"/order/{order_commodity_a}/cancel")

    assert response.status_code == 200
    BaseResponse[None].model_validate(response.json())
    response = authorized_client.get("/order/list")

    assert response.status_code == 200
    data = BaseResponse[list[Order]].model_validate(response.json()).data
    assert data is not None
    order = [item for item in data if item.oid == order_commodity_a]

    assert len(order) == 1 and order[0].status == OrderStatus.Canceled.value


@pytest.mark.order(after="test_all_order")
def test_order_status(authorized_client: TestClient, order_commodity_b: str):
    edit_response = authorized_client.put(
        f"/order/{order_commodity_b}", params={"status": OrderStatus.Shipped.value}
    )

    assert edit_response.status_code == 200
    BaseResponse[None].model_validate(edit_response.json())

    get_response = authorized_client.get("/order/list")
    assert get_response.status_code == 200
    data = BaseResponse[list[Order]].model_validate(get_response.json()).data
    assert data is not None

    order = [item for item in data if item.oid == order_commodity_b]
    assert len(order) == 1 and order[0].status == OrderStatus.Shipped.value
