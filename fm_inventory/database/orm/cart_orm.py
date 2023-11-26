from fm_inventory.database.orm import AbstractBase
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class CartItem(AbstractBase):
    __tablename__ = "cart_items"
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False)
    is_purchased = Column(Boolean, default=False)
    product = relationship("Product", cascade="all, delete-orphan", single_parent=True)
    cart = relationship(
        "Cart",
        back_populates="items",
        cascade="all, delete-orphan",
        single_parent=True,
    )


class Cart(AbstractBase):
    __tablename__ = "carts"

    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
    )
