from fastapi import FastAPI

from . import api, dependencies


def create_app() -> FastAPI:
    app = FastAPI(title="Users Microservice", version="0.0.1")
    dependencies.init_app(app)
    api.init_app(app)
    return app
