from . import APIRouter, Body, status, UUID
import fm_inventory.schemas.product_schemas as schemas
import fm_inventory.services.product_service as product_service
from fastapi import Depends

api_router = APIRouter(prefix="/v1/product", tags=["Product Mangement"])


@api_router.post(
    path="", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductProfile
)
async def create_product(product: schemas.Product):
    return await product_service.create_product(product=product)


@api_router.get(
    path="s",
    response_model=schemas.PaginatedProductProfile,
    status_code=status.HTTP_200_OK,
)
async def get_products(
    product_query: schemas.ProductQuery = Depends(schemas.ProductQuery),
):
    return await product_service.get_products(**product_query.model_dump())


@api_router.get(
    path="/{product_id}",
    response_model=schemas.ProductProfile,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: UUID):
    return await product_service.get_product(product_id=product_id)


@api_router.patch(
    path="/{product_id}",
    response_model=schemas.ProductProfile,
    status_code=status.HTTP_200_OK,
)
async def update_product(product_id: UUID, product_update: schemas.ProductUpdate):
    return await product_service.update_product(
        product_id=product_id, product_update=product_update
    )


@api_router.delete(
    path="/{product_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_product(product_id: UUID):
    return await product_service.delete_product(product_id=product_id)
