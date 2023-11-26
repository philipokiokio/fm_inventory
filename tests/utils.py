from faker import Faker
from fm_inventory.schemas import cart_schemas, product_schemas
import random

faker = Faker()


faker["en_US"]


def get_custom_product(quantity: int = None):
    return product_schemas.Product(
        name=faker.company(),
        category=faker.job(),
        quantity=random.randint(1, 100) or quantity,
        price=random.randint(1, 100) * 10000,
        in_stock=True,
        labels=[product_schemas.Label(name=faker.first_name_nonbinary().lower())],
    )
