from datetime import datetime

from bson import ObjectId
from pydantic import Field
from pymongo import IndexModel

from . import schemas


class UserDAO(schemas.User):
    id: str = Field(alias="_id", default_factory=lambda: str(ObjectId()))
    created_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def collection_name(cls) -> str:
        return "users"

    @classmethod
    def indexes(cls) -> list[IndexModel]:
        return [
            IndexModel("name", unique=True),
            IndexModel("cpf", unique=True),
            IndexModel("codEntidade"),
        ]
