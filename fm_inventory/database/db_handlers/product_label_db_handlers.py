from fm_inventory.database.db_handlers import async_session
import logging
from fm_inventory.schemas.product_schemas import (
    ListLabelProfile,
    Product,
    ProductProfile,
    ProductUpdate,
    Label,
    LabelProfile,
    List,
    PaginatedProductProfile,
    StockInfo,
)
from sqlalchemy import update, select, insert, delete
from fm_inventory.database.orm.product_orm import Product as ProductDB
from fm_inventory.database.orm.product_orm import Label as LabelDB
from fm_inventory.database.orm.product_orm import (
    product_label_table as product_label_DB,
)
from fm_inventory.utils.fm_exceptions import (
    CreateError,
    UpdateError,
    DeleteError,
    NotFoundError,
)
from sqlalchemy import and_, func
from uuid import UUID
from sqlalchemy.orm import selectinload

LOGGER = logging.getLogger(__file__)


async def create_product(product: Product, labels: List[LabelProfile] = None):
    async with async_session() as session:
        product_dict = product.model_dump()
        product_dict.pop("labels")

        stmt = insert(ProductDB).values(**product_dict).returning(ProductDB)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error("prodcut was not created")
            session.rollback()
            raise CreateError

        orm_labels = []
        if labels:
            orm_labels = await _get_labels(labels=labels)

            await session.execute(
                product_label_DB.insert().values(
                    [
                        {"product_id": result.id, "label_id": label.id}
                        for label in orm_labels
                    ]
                )
            )

        await session.commit()

        result_dict = result.as_dict()
        result_dict["labels"] = orm_labels
        return ProductProfile(**result_dict)


async def get_products(**kwargs):
    limit = kwargs.get("limit", 50)
    offset = kwargs.get("offset", 0)
    product_name = kwargs.get("product_name")

    filter_arr = []
    if product_name:
        filter_arr.append(ProductDB.name.icontains(product_name))

    async with async_session() as session:
        stmt = (
            select(ProductDB)
            .options(selectinload(ProductDB.labels))
            .where(and_(*filter_arr))
        )
        stmt.limit(limit=limit).offset(offset=offset)
        result = (await session.execute(statement=stmt)).all()

        match_size = (
            await session.execute(
                select(func.count(ProductDB.id)).where(and_(*filter_arr))
            )
        ).scalar()

        if not result:
            return PaginatedProductProfile()

        product_set = []
        for product in result:
            product_: ProductDB = product[0]
            product_dict = product_.as_dict()
            product_dict["labels"] = product_.labels
            product_set.append(product_dict)

        return PaginatedProductProfile(result_size=match_size, result_set=product_set)


async def get_product(product_id: UUID):
    async with async_session() as session:
        stmt = (
            select(ProductDB)
            .options(selectinload(ProductDB.labels))
            .where(ProductDB.id == product_id)
        )
        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            raise NotFoundError

        product_dict = result.as_dict()
        product_dict["labels"] = result.labels
        return ProductProfile(**product_dict)


async def update_product(
    product_id: UUID, product_update: ProductUpdate, labels: List[LabelProfile] = None
):
    async with async_session() as session:
        product_update_dict = product_update.model_dump(
            exclude_none=True, exclude_unset=True
        )
        if product_update.labels:
            product_update_dict.pop("labels")

        stmt = (
            update(ProductDB)
            .where(ProductDB.id == product_id)
            .values(**product_update_dict)
            .options(selectinload(ProductDB.labels))
            .returning(ProductDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            LOGGER.error("product was not updated")
            raise UpdateError

        if product_update.labels:
            orm_labels = await _get_labels(labels=labels)
            # Add new labels
            new_labels = []
            existing_label_ids = {label.id for label in result.labels}

            for label in orm_labels:
                if label.id not in existing_label_ids:
                    new_labels.append(label)

            await session.execute(
                product_label_DB.insert().values(
                    [
                        {"product_id": result.id, "label_id": label.id}
                        for label in new_labels
                    ]
                )
            )
        await session.commit()

        labels = result.labels

        result_dict = result.as_dict()
        result_dict["labels"] = [*labels, *new_labels]
        return ProductProfile(**result_dict)


async def update_product_quantity(product_id: UUID, quantity_to_be_purchased: int):
    async with async_session() as session:
        # Row Lock
        stmt = (
            select(ProductDB)
            .where(ProductDB.id == product_id)
            .with_for_update(of=ProductDB)
        )

        product = (await session.execute(statement=stmt)).scalar_one_or_none()
        # tracker strict update criteria
        update_stmt = (
            update(ProductDB)
            .where(
                and_(ProductDB.id == product_id, ProductDB.tracker == product.tracker)
            )
            .values(
                quantity=product.quantity - quantity_to_be_purchased,
                version=ProductDB.tracker + 1,
            )
            .returning(ProductDB)
        )
        result = (await session.execute(statement=update_stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            LOGGER.error("product was not updated")
            raise UpdateError

        # releasing the lock after a completed transaction
        await session.commit()

        return ProductProfile(**result.as_dict())


async def delete_product(product_id: UUID):
    async with async_session() as session:
        stmt = (
            select(ProductDB)
            .options(selectinload(ProductDB.labels))
            .where(ProductDB.id == product_id)
        )
        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        await session.delete(result)
        await session.commit()
        return ProductProfile(**result.as_dict())


# Label Action
async def create_label(labels: List[Label]):
    async with async_session() as session:
        stmt = (
            insert(LabelDB)
            .values([label.model_dump() for label in labels])
            .returning(LabelDB)
        )
        (await session.execute(statement=stmt))

        await session.commit()

        result = await _get_labels(labels=labels)

        return ListLabelProfile(result_set=[x.as_dict() for x in result])


async def _get_labels(labels: List[Label]):
    async with async_session() as session:
        added_label_names = [label.name for label in labels]

        get_stmt = select(LabelDB).where(LabelDB.name.in_(added_label_names))

        result = (await session.execute(statement=get_stmt)).scalars().all()
        return result


async def get_labels(labels: List[Label]):
    result = await _get_labels(labels=labels)

    if not result:
        return {}

    return {res.name: LabelProfile(**res.as_dict()) for res in result}

    ...
