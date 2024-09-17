from fastapi import APIRouter

# from ...dependencies.auth import login
from . import controller, models, schemas

router = APIRouter()
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=201)
def create_user(user: schemas.User) -> models.UserDAO:
    return controller.create_user(user)


@router.get("/{user_id}", status_code=200)
def get_user(user_id: str):
    return controller.read_user(user_id)


@router.get("/{role}/{codEntidade}", status_code=200)
def get_users(
    role: str,
    codEntidade: str,
):
    return controller.read_users(role, codEntidade)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str):
    controller.delete_user(user_id)
