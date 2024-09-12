from fastapi import FastAPI

from . import health


def init_app(app: FastAPI) -> None:
    app.include_router(health.router)
