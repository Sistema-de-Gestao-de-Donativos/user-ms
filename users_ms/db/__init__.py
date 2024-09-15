from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorDatabase
# import controller
from ..api.users import controller

from .users import models


async def init_db(database: AsyncIOMotorDatabase) -> None:
    await init_beanie(database=database, document_models=[models.User],)
    controller.insert_user(models.User(first_name="Vinicius", last_name="Turani", role="superadmin", email="viniconteturani@gmail.com"))
    print("DB initialized")
