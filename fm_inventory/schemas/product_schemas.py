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
from datetime import datetime
from enum import Enum


class StockInfo(Enum):
    out_of_stock: str = "Out of Stock"
    available: str = "Available"


class name(AbstractModel):
    name: str


class Label(name):
    ...


class LabelProfile(Label):
    id: UUID


class ListLabelProfile(AbstractModel):
    result_set: conlist(item_type=LabelProfile, min_length=1) = []


class Product(name):
    category: str  # This could be scoped by an Enum
    # giving an allowed category rather than a category
    quantity: min_of_zero
    price: min_of_one
    in_stock: bool
    labels: Optional[List[Label]] = None

    @model_validator(mode="after")
    def product_available_validator(self):
        quantity = self.quantity
        in_stock = self.in_stock
        if quantity == 0 and in_stock:
            self.in_stock = False
        return self


class ProductUpdate(AbstractModel):
    name: Optional[str] = None
    category: Optional[str] = None  # This could be scoped by an Enum
    # giving an allowed category rather than a category
    quantity: Optional[min_of_zero] = None
    price: Optional[min_of_one] = None
    in_stock: Optional[bool] = None
    labels: Optional[List[Label]] = None

    @model_validator(mode="after")
    def product_available_validator(self):
        quantity = self.quantity
        if quantity == 0:
            self.in_stock = False
        return self


class ProductProfile(Product):
    id: UUID
    date_created_utc: datetime


class PaginatedProductProfile(AbstractModel):
    result_size: min_of_zero = 0
    result_set: conlist(item_type=ProductProfile, min_length=1) = []


class ProductQuery(AbstractModel):
    limit: int = 50
    offset: int = 0
    product_name: Optional[str] = None
