from fm_inventory.schemas.cart_schemas import Users
import tests.utils as general_utils
from fastapi.testclient import TestClient
from uuid import UUID


def create_product(test_client: TestClient, quantity: int = None):
    custom_product = general_utils.get_custom_product(quantity=quantity)
    response = test_client.post(url="/v1/product", json=custom_product.model_dump())

    return response.json()


def create_cart(app_test_client_fixture: TestClient):
    response = app_test_client_fixture.get(url=f"/v1/cart?user={Users.ab_soul.value}")

    return response.json()


def get_product(product_id: UUID, app_test_client_fixture: TestClient):
    response = app_test_client_fixture.get(url=f"/v1/product/{product_id}")

    return response.json()


def product_out_of_stock(app_test_client_fixture: TestClient):
    new_product = create_product(test_client=app_test_client_fixture)

    response = app_test_client_fixture.patch(
        url=f"/v1/product/{new_product['id']}", json={"quantity": 0}
    )

    return response.json()
