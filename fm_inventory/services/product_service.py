import fm_inventory.database.db_handlers.product_label_db_handlers as product_db_handler
import fm_inventory.schemas.product_schemas as schemas
import logging
from typing import List
import fm_inventory.services.label_service as label_service
from uuid import UUID
from fastapi import HTTPException, status
from fm_inventory.utils.fm_exceptions import CreateError, NotFoundError, UpdateError

LOGGER = logging.getLogger(__name__)


async def get_labels(labels: List[schemas.Label]):
    label_profiles = []
    if labels:
        label_profiles = await label_service.upsert_label(labels=labels)
    return label_profiles


async def create_product(product: schemas.Product):
    try:
        label_profiles = []
        if product.labels:
            label_profiles = await get_labels(labels=product.labels)

        product_profile = await product_db_handler.create_product(
            product=product, labels=label_profiles if product.labels else None
        )

        return product_profile
    except CreateError as e:
        LOGGER.exception(e)
        raise HTTPException(status_code=500, detail="Unexplainable error")


async def get_products(**kwargs):
    return await product_db_handler.get_products(**kwargs)
    ...


async def get_product(product_id: UUID):
    try:
        return await product_db_handler.get_product(product_id=product_id)
    except NotFoundError as e:
        LOGGER.exception(e)
        LOGGER.error(f"no product with {product_id}")
        raise HTTPException(
            detail="product not found", status_code=status.HTTP_404_NOT_FOUND
        )


async def update_product(product_id: UUID, product_update: schemas.ProductUpdate):
    await get_product(product_id=product_id)

    try:
        label_profiles = []
        if product_update.labels:
            # label processing
            label_profiles = await get_labels(labels=product_update.labels)

        return await product_db_handler.update_product(
            product_id=product_id,
            product_update=product_update,
            labels=label_profiles if product_update.labels else None,
        )

    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error(f"product with {product_id} did not update sucessfully")
        raise HTTPException(status_code=500, detail="Unexplainable error")


async def delete_product(product_id: UUID):
    await get_product(product_id=product_id)

    await product_db_handler.delete_product(product_id=product_id)
    return {}


# Product Guard


async def product_cart_processor(product_id: UUID, quantity: int):
    product_profile = await get_product(product_id=product_id)

    if product_profile.quantity == 0 and quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="product is out of stock"
        )
    elif abs(quantity) > product_profile.quantity and quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{abs(quantity)} is greater than the available product quantity: {product_profile.quantity}",
        )

    return await product_db_handler.update_product_quantity(
        product_id=product_id, quantity_to_be_purchased=quantity
    )
