from fastapi.testclient import TestClient
import pytest
import tests.integration.utils as router_utils
import tests.utils as general_utils
from uuid import uuid4

PRODUCT_ROUTE = "/v1/product"


def test_create_product(app_test_client_fixture: TestClient):
    custom_product = general_utils.get_custom_product()
    response = app_test_client_fixture.post(
        url=PRODUCT_ROUTE, json=custom_product.model_dump()
    )

    assert response.status_code == 201

    response_json = response.json()
    response_json.pop("id")
    response_json.pop("date_created_utc")

    assert custom_product.model_dump() == response_json

    ...


def test_get_products_happy_path(app_test_client_fixture: TestClient):
    product_arr = []
    for _ in range(10):
        new_product = router_utils.create_product(test_client=app_test_client_fixture)
        product_arr.append(new_product)

    response = app_test_client_fixture.get(url=f"{PRODUCT_ROUTE}s")
    assert response.status_code == 200

    response_json = response.json()

    assert response_json["result_size"] == 10
    assert response_json["result_set"] == product_arr


def test_get_products_sad_path(app_test_client_fixture: TestClient):
    response = app_test_client_fixture.get(url=f"{PRODUCT_ROUTE}s")
    assert response.status_code == 200

    response_json = response.json()

    assert response_json["result_size"] == 0
    assert response_json["result_set"] == []


def test_get_product_happy_path(app_test_client_fixture: TestClient):
    new_product = router_utils.create_product(test_client=app_test_client_fixture)

    response = app_test_client_fixture.get(url=f"{PRODUCT_ROUTE}/{new_product['id']}")
    assert response.status_code == 200

    response_json = response.json()

    assert response_json == new_product


def test_get_product_sad_path(app_test_client_fixture: TestClient):
    response = app_test_client_fixture.get(url=f"{PRODUCT_ROUTE}/{str(uuid4())}")
    assert response.status_code == 404

    response_json = response.json()

    assert response_json["detail"] == "product not found"


def test_update_product_happy_path(app_test_client_fixture: TestClient):
    new_product = router_utils.create_product(test_client=app_test_client_fixture)

    response = app_test_client_fixture.patch(
        url=f"{PRODUCT_ROUTE}/{new_product['id']}", json={"quantity": 100}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["quantity"] == 100
    assert response_json != new_product


def test_update_product_happy_path(app_test_client_fixture: TestClient):
    new_product = router_utils.create_product(test_client=app_test_client_fixture)

    response = app_test_client_fixture.delete(
        url=f"{PRODUCT_ROUTE}/{new_product['id']}"
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json == {}
