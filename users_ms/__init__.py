from fastapi import FastAPI

from . import dependencies, routes
from .settings import Settings


def create_app() -> FastAPI:
    sets = Settings()  # type: ignore

    app = FastAPI(
        title="Users Microservice",
        version="0.0.1",
    )

    # dependencies.init_app(app, sets)
    routes.init_app(app)

    return app
