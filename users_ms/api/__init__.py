from fastapi import APIRouter, Depends, FastAPI
from .users.auth.auth import login
from . import users

def init_app(app: FastAPI) -> None:
    router = get_router()
    app.include_router(router)

def get_router() -> APIRouter:
    api_router = APIRouter(prefix="/api", dependencies=[Depends(login)])
    api_router.include_router(users.router)
    return api_router
