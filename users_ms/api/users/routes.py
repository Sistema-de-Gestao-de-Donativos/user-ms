from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException

from ...api.users.auth.auth import auth_router

from ...db.users import models, schemas
from . import controller

router = APIRouter(prefix="/users", tags=["Users"])

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])

@router.get("", status_code=200)
async def get_all_users() -> list[models.User]:
    return await controller.get_all_users()


@router.get("/{user_id}", status_code=200)
async def get_user(user_id: PydanticObjectId) -> models.User:
    user = await controller.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", status_code=201)
async def create_user(user: schemas.User) -> None:
    inserted = await controller.insert_user(user)
    if not inserted:
        raise HTTPException(status_code=400, detail="User already exists")


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: PydanticObjectId) -> None:
    deleted = await controller.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")


@router.put("/{user_id}", status_code=200)
async def update_user(user_id: PydanticObjectId, user: schemas.User) -> None:
    updated = await controller.update_user(user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")


@router.patch("/{user_id}", status_code=200)
async def patch_user(user_id: PydanticObjectId, user: schemas.PatchUser) -> None:
    patched = await controller.patch_user(user_id, user)
    if not patched:
        raise HTTPException(status_code=404, detail="User not found")
