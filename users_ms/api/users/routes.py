from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from . import controller, models, schemas

router = APIRouter()
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=201)
def create_user(
    request: Request,
    user: schemas.User,
) -> models.UserDAO:
    allowed_roles = ["superadmin"]
    if request.state.user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Forbidden")

    return controller.create_user(user)


@router.get("/{user_id}", status_code=200)
def get_user(user_id: str):
    return controller.read_user(user_id)


@router.get("/", status_code=200)
def read_many(
    request: Request,
    user_id: Optional[str] = None,
    role: Optional[str] = None,
    codEntidade: Optional[int] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
):
    allowed_roles = ["superadmin"]
    if request.state.user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Forbidden")

    return controller.read_many(user_id, role, codEntidade, phone, email)


@router.get("/{role}/{codEntidade}", status_code=200)
def get_users(
    request: Request,
    role: str,
    codEntidade: int,
):
    allowed_roles = ["superadmin"]
    if request.state.user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    return controller.read_users(role, codEntidade)


@router.delete("/{user_id}", status_code=204)
def delete_user(request: Request, user_id: str):
    allowed_roles = ["superadmin"]
    if request.state.user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Forbidden")

    controller.delete_user(user_id)
