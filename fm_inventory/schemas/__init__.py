from fm_inventory.utils.base_schemas import AbstractModel
from pydantic import conint, conlist, model_validator
from typing import Optional, List
from uuid import UUID


# INT that has to be greater or equal to 1
min_of_one = conint(ge=1)
min_of_zero = conint(ge=0)
