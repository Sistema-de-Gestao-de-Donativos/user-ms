from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorDatabase

from .users import models


async def init_db(database: AsyncIOMotorDatabase) -> None:
    await init_beanie(database=database, document_models=[models.User])
