from . import APIRouter, Body, status, UUID
import fm_inventory.schemas.cart_schemas as schemas
import fm_inventory.services.cart_service as cart_service
from fastapi import Depends

api_router = APIRouter(prefix="/v1/cart", tags=["Cart Management"])


# CART
@api_router.get(
    path="", response_model=schemas.CartProfile, status_code=status.HTTP_200_OK
)
async def get_cart(user: schemas.Users):
    return await cart_service.upsert_cart(user_uid=user.value)


@api_router.post(
    path="/puchase", response_model=schemas.CartProfile, status_code=status.HTTP_200_OK
)
async def purchase_items_in_cart(user: schemas.Users):
    return await cart_service.purchase_items_in_cart(user_uid=user.value)


# CART_ITEM


@api_router.post(
    path="/add-item",
    response_model=schemas.CartItemProfile,
    status_code=status.HTTP_201_CREATED,
)
async def add_item(cart_item: schemas.CartItem, user: schemas.Users):
    return await cart_service.add_to_cart(user_uid=user.value, cart_item=cart_item)


@api_router.delete(path="/remove-item/{cart_item_id}", status_code=status.HTTP_200_OK)
async def remove_item(cart_item_id: UUID, user: schemas.Users):
    return await cart_service.remove_item(
        user_uid=user.value, cart_item_id=cart_item_id
    )
