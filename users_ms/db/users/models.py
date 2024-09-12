from datetime import datetime

from beanie import Document
from pydantic import Field

from . import schemas


class BaseUser(Document):
    created_at: datetime = Field(default_factory=datetime.now)


class User(schemas.User, BaseUser):
    class Settings:
        name = "users"
