from fastapi.testclient import TestClient
import pytest
import tests.integration.utils as router_utils
import tests.utils as general_utils
from fm_inventory.schemas.cart_schemas import Users

from uuid import uuid4


CART_ROUTE = "/v1/cart"


def test_get_empty_cart_sad_path(app_test_client_fixture: TestClient):
    response = app_test_client_fixture.get(url=f"{CART_ROUTE}?user={str(uuid4())}")

    assert response.status_code == 422


def test_get_empty_cart_happy_path(app_test_client_fixture: TestClient):
    response = app_test_client_fixture.get(
        url=f"{CART_ROUTE}?user={Users.ab_soul.value}"
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["total"] == 0
    assert response_json["items"] == []


def test_purchase_items_in_cart_sad_path_no_cart(app_test_client_fixture: TestClient):
    response = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/puchase?user={Users.ab_soul.value}"
    )

    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "no cart for this user"


def test_purchase_items_in_cart_sad_path(app_test_client_fixture: TestClient):
    router_utils.create_cart(app_test_client_fixture=app_test_client_fixture)

    response = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/puchase?user={Users.ab_soul.value}"
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "cart is empty"


def test_add_product_to_cart(app_test_client_fixture: TestClient):
    product = router_utils.create_product(test_client=app_test_client_fixture)
    router_utils.create_cart(app_test_client_fixture=app_test_client_fixture)

    response = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/add-item?user={Users.ab_soul.value}",
        json={"product_id": product["id"], "quantity": 2},
    )
    updated_product = router_utils.get_product(
        product_id=product["id"], app_test_client_fixture=app_test_client_fixture
    )
    assert response.status_code == 201
    assert product["quantity"] != updated_product["quantity"]
    assert updated_product["quantity"] == product["quantity"] - 2


def test_add_product_to_cart_sad_path(app_test_client_fixture: TestClient):
    router_utils.create_cart(app_test_client_fixture=app_test_client_fixture)

    response = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/add-item?user={Users.ab_soul.value}",
        json={"product_id": str(uuid4()), "quantity": 2},
    )
    response_json = response.json()

    assert response.status_code == 404
    assert response_json["detail"] == "product not found"


def test_add_product_to_cart_overdraft_sad_path(app_test_client_fixture: TestClient):
    router_utils.create_cart(app_test_client_fixture=app_test_client_fixture)
    product = router_utils.create_product(test_client=app_test_client_fixture)

    response = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/add-item?user={Users.ab_soul.value}",
        json={"product_id": product["id"], "quantity": 20000},
    )
    response_json = response.json()

    assert response.status_code == 400
    assert (
        response_json["detail"]
        == f"20000 is greater than the available product quantity: {product['quantity']}"
    )


def test_add_product_to_cart_out_of_stock_sad_path(app_test_client_fixture: TestClient):
    router_utils.create_cart(app_test_client_fixture=app_test_client_fixture)
    product = router_utils.product_out_of_stock(
        app_test_client_fixture=app_test_client_fixture
    )

    response = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/add-item?user={Users.ab_soul.value}",
        json={"product_id": product["id"], "quantity": 20000},
    )
    response_json = response.json()

    assert response.status_code == 400
    assert response_json["detail"] == "product is out of stock"


def test_purchase_items_in_cart_happy_path(app_test_client_fixture: TestClient):
    product = router_utils.create_product(test_client=app_test_client_fixture)
    router_utils.create_cart(app_test_client_fixture=app_test_client_fixture)

    response = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/add-item?user={Users.ab_soul.value}",
        json={"product_id": product["id"], "quantity": 2},
    )
    updated_product = router_utils.get_product(
        product_id=product["id"], app_test_client_fixture=app_test_client_fixture
    )
    assert response.status_code == 201
    assert product["quantity"] != updated_product["quantity"]
    assert updated_product["quantity"] == product["quantity"] - 2

    response = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/puchase?user={Users.ab_soul.value}"
    )

    response_json = response.json()

    assert response.status_code == 200

    assert response_json["total"] == 0
    assert (
        response_json["items"][0]["product"]["quantity"] == updated_product["quantity"]
    )


def test_get_cart_filled_happy_path(app_test_client_fixture: TestClient):
    product = router_utils.create_product(test_client=app_test_client_fixture)
    router_utils.create_cart(app_test_client_fixture=app_test_client_fixture)

    response = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/add-item?user={Users.ab_soul.value}",
        json={"product_id": product["id"], "quantity": 2},
    )
    updated_product = router_utils.get_product(
        product_id=product["id"], app_test_client_fixture=app_test_client_fixture
    )
    assert response.status_code == 201
    assert product["quantity"] != updated_product["quantity"]
    assert updated_product["quantity"] == product["quantity"] - 2

    response = app_test_client_fixture.get(
        url=f"{CART_ROUTE}?user={Users.ab_soul.value}"
    )

    response_json = response.json()

    assert response.status_code == 200

    assert response_json["total"] == updated_product["price"] * 2
    assert (
        response_json["items"][0]["product"]["quantity"] == updated_product["quantity"]
    )


def test_remove_item_from_cart_happy_path(app_test_client_fixture: TestClient):
    product = router_utils.create_product(test_client=app_test_client_fixture)
    router_utils.create_cart(app_test_client_fixture=app_test_client_fixture)

    added_item = app_test_client_fixture.post(
        url=f"{CART_ROUTE}/add-item?user={Users.ab_soul.value}",
        json={"product_id": product["id"], "quantity": 2},
    )
    updated_product = router_utils.get_product(
        product_id=product["id"], app_test_client_fixture=app_test_client_fixture
    )
    assert added_item.status_code == 201
    assert product["quantity"] != updated_product["quantity"]
    assert updated_product["quantity"] == product["quantity"] - 2

    added_item = added_item.json()

    response = app_test_client_fixture.delete(
        url=f"{CART_ROUTE}/remove-item/{added_item['id']}?user={Users.ab_soul.value}"
    )

    response_json = response.json()
    updated_product = router_utils.get_product(
        product_id=product["id"], app_test_client_fixture=app_test_client_fixture
    )
    assert response.status_code == 200
    assert response_json == {}
    assert product == updated_product
