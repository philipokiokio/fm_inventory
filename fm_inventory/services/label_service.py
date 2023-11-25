import fm_inventory.database.db_handlers.product_label_db_handlers as label_db_handler
import fm_inventory.schemas.product_schemas as label_schemas
import logging
from typing import List


LOGGER = logging.getLogger(__name__)


async def create_label(labels: List[label_schemas.Label]):
    return await label_db_handler.create_label(labels=labels)


async def upsert_label(labels: List[label_schemas.Label]):
    not_created_label = []

    bleached_labels = [label_schemas.Label(name=label.name.lower()) for label in labels]
    label_set = await label_db_handler.get_labels(labels=bleached_labels)

    for label in bleached_labels:
        if not label_set.get(label.name):
            not_created_label.append(label)

    created_label_profile = []
    if len(not_created_label) > 0:
        created_label_profile = await create_label(labels=not_created_label)
        created_label_profile = created_label_profile.result_set

    label_profiles = list(label_set.values())
    return [*created_label_profile, *label_profiles]
