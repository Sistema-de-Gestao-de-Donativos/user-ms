import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..db import init_db
from ..settings import Settings

sets = Settings()  # type: ignore

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


logger = logging.getLogger(__name__)


async def connect() -> None:
    logger.info("Connecting to database...")
    global client, database
    client = AsyncIOMotorClient(sets.MONGO_DB_URL)
    database = client[sets.MONGO_DB_NAME]
    await init_db(database)
    logger.info("Connected to database!")


def shutdown() -> None:
    logger.info("Disconnecting database...")
    if client is not None:
        client.close()
    logger.info("Disconnected database!")
