from fm_inventory.schemas import (
    AbstractModel,
    min_of_one,
    min_of_zero,
    Optional,
    conlist,
    model_validator,
    List,
    UUID,
)
from fm_inventory.schemas.product_schemas import ProductProfile
from enum import Enum


class CartItem(AbstractModel):
    product_id: UUID
    quantity: min_of_one


class CartItemProfile(CartItem):
    id: UUID
    product: Optional[ProductProfile] = None


class CartProfile(AbstractModel):
    id: UUID
    items: List[CartItemProfile] = []
    total: min_of_zero = 0


class Users(Enum):
    kendrick = "45fed603-dcf1-43a5-b4e9-1a52902eab0e"
    ab_soul = "25b99961-7378-4779-bc0f-62577b5d5de8"
    cole = "d649792d-c7fd-41d6-9b11-8d1c6b39683d"
    drake = "4a21e05a-ac64-4527-806e-c3140761496d"
