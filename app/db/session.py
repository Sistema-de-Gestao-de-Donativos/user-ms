from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from typing import Annotated

from utils.config import DB_SCRIPT_SQLITE
from auth.env import get_db_env


Base = declarative_base()


def get_db():
    db_env = get_db_env()
    db_script = db_env.get("Script")
    db_url = db_env.get("URL")

    if db_script == DB_SCRIPT_SQLITE:
        engine = create_engine(
            db_url, connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(db_url)
        if not database_exists(engine.url):
            create_database(engine.url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Database = Annotated[Session, Depends(get_db)]
