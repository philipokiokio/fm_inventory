from .utils.base_schemas import AbstractSettings
from pydantic.networks import PostgresDsn
from pydantic import EmailStr


class Settings(AbstractSettings):
    postgres_url: PostgresDsn
    mail_username: str
    mail_password: str
    mail_from: EmailStr
    mail_from_name: str
    mail_port: int
    mail_server: str
