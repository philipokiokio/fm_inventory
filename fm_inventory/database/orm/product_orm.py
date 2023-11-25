from fm_inventory.database.orm import AbstractBase, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, String, Table, ForeignKey, Integer, Boolean, BigInteger
from sqlalchemy.orm import relationship
from fm_inventory.database_conf import Base

product_label_table = Table(
    "product_label",
    AbstractBase.metadata,
    Column("label_id", UUID, ForeignKey("labels.id")),
    Column("product_id", UUID, ForeignKey("products.id")),
)


class Label(AbstractBase):
    __tablename__ = "labels"
    name = Column(String, nullable=False, unique=True)
    product = relationship(
        "Product", secondary=product_label_table, back_populates="labels"
    )


class Product(AbstractBase):
    __tablename__ = "products"
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Integer, nullable=False)
    in_stock = Column(Boolean, default=False)
    tracker = Column(BigInteger, default=1)
    labels = relationship(
        "Label", secondary=product_label_table, back_populates="product"
    )
