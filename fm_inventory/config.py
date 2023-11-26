from .utils.base_schemas import AbstractSettings
from pydantic.networks import PostgresDsn
from pydantic import EmailStr


class Settings(AbstractSettings):
    postgres_url: PostgresDsn
