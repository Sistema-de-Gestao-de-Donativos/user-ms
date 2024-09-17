from typing import Optional

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from ..utils import get_collection
from .models import UserDAO
from .schemas import User


def create_user(user: User) -> UserDAO:
    user_dao = UserDAO(**user.model_dump())
    collection = get_collection(UserDAO.collection_name())
    try:
        collection.insert_one(user_dao.model_dump(by_alias=True))
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="User already exists")

    return user_dao


def read_user(user_id: str) -> UserDAO:
    collection = get_collection(UserDAO.collection_name())
    user = collection.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserDAO(**user)


def read_many(
    user_id: Optional[str],
    role: Optional[str],
    codEntidade: Optional[int],
    phone: Optional[str],
    email: Optional[str],
):
    collection = get_collection(UserDAO.collection_name())
    filters = {}
    if user_id:
        filters["_id"] = user_id
    if role:
        filters["role"] = role
    if codEntidade:
        filters["codEntidade"] = codEntidade
    if phone:
        filters["phone"] = phone
    if email:
        filters["email"] = email

    users = collection.find(filters)
    return [UserDAO(**user) for user in users]


def read_users(role: str, codEntidade: int) -> list[UserDAO]:
    collection = get_collection(UserDAO.collection_name())
    users = collection.find({"role": role, "codEntidade": codEntidade})
    return [UserDAO(**user) for user in users]


def delete_user(user_id: str) -> None:
    collection = get_collection(UserDAO.collection_name())
    collection.delete_one({"_id": user_id})
    collection.delete_one({"_id": user_id})
