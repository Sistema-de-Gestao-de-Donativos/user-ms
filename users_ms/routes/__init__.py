from fastapi import APIRouter, FastAPI


def init_app(app: FastAPI) -> None:
    router = APIRouter()
    app.include_router(router)
