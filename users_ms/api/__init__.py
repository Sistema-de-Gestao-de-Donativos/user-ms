from fastapi import APIRouter, FastAPI

from . import health, users


def init_app(app: FastAPI) -> None:
    router = get_router()
    app.include_router(router)


def get_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(health.health_router)
    api_router.include_router(users.users_router)
    return api_router
