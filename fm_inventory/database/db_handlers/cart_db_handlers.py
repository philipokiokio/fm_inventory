from fm_inventory.database.db_handlers import async_session
import logging
from fm_inventory.schemas.cart_schemas import CartItem, CartItemProfile, CartProfile

from sqlalchemy import update, select, insert, delete
from fm_inventory.database.orm.cart_orm import CartItem as CartItemDB
from fm_inventory.database.orm.cart_orm import Cart as CartDB
from sqlalchemy import and_
from uuid import UUID
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from fm_inventory.utils.fm_exceptions import (
    CreateError,
    DeleteError,
    NotFoundError,
    UpdateError,
)

LOGGER = logging.getLogger(__file__)

# CART'


async def create_cart(user_uid: UUID):
    async with async_session() as session:
        stmt = insert(CartDB).values(user_id=user_uid).returning(CartDB)

        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()

            if not result:
                LOGGER.error(f"record failed to create for {user_uid}")
                await session.rollback()
                raise CreateError
        except IntegrityError as e:
            LOGGER.exception(e)
            LOGGER.error(f"{user_uid} has cart record")
            await session.rollback()

        await session.commit()
        return CartProfile(**result.as_dict())


async def get_cart(user_uid: UUID):
    async with async_session() as session:
        stmt = (
            select(CartDB)
            .where(CartDB.user_id == user_uid)
            .options(selectinload(CartDB.items).selectinload(CartItemDB.product))
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()
        if not result:
            LOGGER.error(f"No cart found for user with id: {user_uid}")
            raise NotFoundError
        cart_items = result.items

        items = []

        for item in cart_items:
            if item.is_purchased == False:
                item_dict = item.as_dict()
                item_dict["product"] = item.product.as_dict()
                items.append(item_dict)

        cart = result.as_dict()

        return CartProfile(**cart, items=items)


async def purchase_items_in_cart(cart_id: UUID):
    async with async_session() as session:
        stmt = (
            update(CartDB)
            .where(and_(CartDB.id == cart_id))
            .options(selectinload(CartDB.items))
            .returning(CartDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(f"record for cart with id:{cart_id} was not updated")
            await session.rollback()
            raise UpdateError
        for cart_item in result.items:
            cart_item.is_purchased = True

        await session.commit()

        cart_items = result.items

        items = []

        for item in cart_items:
            item_dict = item.as_dict()
            item_dict["product"] = item.product.as_dict()
            items.append(item_dict)

        cart = result.as_dict()
        return CartProfile(**cart, items=items)


# CART ITEMS


async def add_to_cart(cart_id: UUID, cart_item: CartItem):
    async with async_session() as session:
        stmt = (
            insert(CartItemDB)
            .values(**cart_item.model_dump(), cart_id=cart_id)
            .returning(CartItemDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(f"failed to add an item  to a cart with id: {cart_id}")
            await session.rollback()
            raise CreateError

        await session.commit()

        # Fetch the associated Product information
        loaded_result = (
            await session.execute(
                select(CartItemDB)
                .where(CartItemDB.id == result.id)
                .options(selectinload(CartItemDB.product))
            )
        ).scalar_one()
        product = loaded_result.product
        return CartItemProfile(**loaded_result.as_dict(), product=product.as_dict())


async def remove_item(cart_item_id: UUID, cart_id: UUID):
    async with async_session() as session:
        stmt = (
            delete(CartItemDB)
            .where(and_(CartItemDB.id == cart_item_id, CartItemDB.cart_id == cart_id))
            .options(selectinload(CartItemDB.product))
            .returning(CartItemDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(
                f"record fo item: {cart_item_id}\
                 was not found or deleted"
            )
            await session.rollback()
            raise DeleteError

        await session.commit()
        product = result.product

        return CartItemProfile(**result.as_dict(), product=product.as_dict())


# What can still be done.
# the ability to increase or decrease the quantity of items in the cart.
