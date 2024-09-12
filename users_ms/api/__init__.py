from fastapi import APIRouter, Depends, FastAPI

from ..dependencies.security import validate_api_key
from . import users


def init_app(app: FastAPI) -> None:
    router = get_router()
    app.include_router(router)


def get_router() -> APIRouter:
    api_router = APIRouter(prefix="/api", dependencies=[Depends(validate_api_key)])
    api_router.include_router(users.router)
    return api_router
