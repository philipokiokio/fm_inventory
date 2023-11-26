import fm_inventory.database.db_handlers.cart_db_handlers as cart_db_handlers
import fm_inventory.schemas.cart_schemas as schemas
import logging
from uuid import UUID
from fastapi import HTTPException, status
from fm_inventory.utils.fm_exceptions import (
    CreateError,
    DeleteError,
    UpdateError,
    NotFoundError,
)
import fm_inventory.services.product_service as product_service

LOGGER = logging.getLogger(__name__)


def unexpected_error():
    raise HTTPException(status_code=500, detail="unexpected error")


# CART CENTRIC
async def get_cart(user_uid: UUID):
    try:
        cart_profile = await cart_db_handlers.get_cart(user_uid=user_uid)
        total_price = 0

        for item in cart_profile.items:
            total_price += item.quantity * item.product.price

        cart_profile.total = total_price
        return cart_profile
    except NotFoundError as e:
        LOGGER.exception(e)
        LOGGER.error(f"There is no cart for user with id: {user_uid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no cart for this user"
        )


async def upsert_cart(user_uid: UUID):
    try:
        return await get_cart(user_uid=user_uid)

    except HTTPException:
        return await create_cart(user_uid=user_uid)


async def create_cart(user_uid: UUID):
    try:
        return await cart_db_handlers.create_cart(user_uid=user_uid)
    except CreateError:
        LOGGER.error("Cart failed to create")
        unexpected_error()


async def purchase_items_in_cart(user_uid: UUID):
    cart_profile = await get_cart(user_uid=user_uid)
    if not cart_profile.items:
        raise HTTPException(
            detail="cart is empty", status_code=status.HTTP_400_BAD_REQUEST
        )

    return await cart_db_handlers.purchase_items_in_cart(cart_id=cart_profile.id)


# CART ITEMS
async def add_to_cart(user_uid: UUID, cart_item: schemas.CartItem):
    cart_profile = await get_cart(user_uid=user_uid)

    try:
        # remove from the quantity from the product
        await product_service.product_cart_processor(
            product_id=cart_item.product_id, quantity=0 - cart_item.quantity
        )
        return await cart_db_handlers.add_to_cart(
            cart_id=cart_profile.id, cart_item=cart_item
        )

    except CreateError:
        LOGGER.error(
            f"{cart_item.model_dump()} failed to be added as a record for cart_id: {cart_profile.id}"
        )
        unexpected_error()


async def remove_item(user_uid: UUID, cart_item_id: UUID):
    cart_profile = await get_cart(user_uid=user_uid)
    try:
        cart_item_profile = await cart_db_handlers.remove_item(
            cart_item_id=cart_item_id, cart_id=cart_profile.id
        )
        # add back to the product
        await product_service.product_cart_processor(
            product_id=cart_item_profile.product_id, quantity=cart_item_profile.quantity
        )
        return {}

    except DeleteError:
        LOGGER.error(
            f"error for deleting row for {cart_profile.id}, and item_id {cart_item_id}"
        )
        raise HTTPException(detail="item not found", status_code=404)
