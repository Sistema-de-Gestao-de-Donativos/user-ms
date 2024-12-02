from fastapi import FastAPI

from . import auth, db


def init_app(app: FastAPI) -> None:
    db.init_app()
    auth.init_app(app)
