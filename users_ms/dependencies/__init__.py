from fastapi import FastAPI

from . import db

# from . import auth


def init_app(app: FastAPI) -> None:
    db.init_app()
