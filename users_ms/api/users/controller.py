from beanie import PydanticObjectId

from ...db.users import models, schemas


async def get_user(user_id: PydanticObjectId) -> models.User | None:
    return await models.User.get(user_id)


async def get_all_users() -> list[models.User]:
    return await models.User.all().to_list()


async def insert_user(user: schemas.User) -> bool:
    new_user = models.User(**user.model_dump())
    try:
        await new_user.save()
        return True
    except Exception:
        return False


async def delete_user(user_id: PydanticObjectId) -> bool:
    user = await models.User.get(user_id)
    if user:
        await user.delete()
        return True
    return False


async def update_user(user_id: PydanticObjectId, user: schemas.User) -> bool:
    old_user: models.User | None = await models.User.get(user_id)
    if old_user:
        for field, value in user.model_dump().items():
            setattr(old_user, field, value)
        await old_user.save()
        return True
    return False


async def patch_user(user_id: PydanticObjectId, user: schemas.PatchUser) -> bool:
    old_user: models.User | None = await models.User.get(user_id)
    if old_user:
        for field, value in user.model_dump(exclude_unset=True).items():
            setattr(old_user, field, value)
        await old_user.save()
        return True
    return False
