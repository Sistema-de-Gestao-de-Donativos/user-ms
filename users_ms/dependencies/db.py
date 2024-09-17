import contextlib

from loguru import logger
from pymongo.errors import DuplicateKeyError, OperationFailure

from users_ms.api.users.models import UserDAO
from users_ms.api.utils import get_collection


def create_indexes():
    collection = get_collection(UserDAO.collection_name())

    with contextlib.suppress(DuplicateKeyError, OperationFailure):
        collection.create_indexes(UserDAO.indexes())

    logger.info("Indexes created")


def init_app() -> None:
    create_indexes()
    logger.info("DB initialized")
