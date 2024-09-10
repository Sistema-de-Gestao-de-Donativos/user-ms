from sqlalchemy.orm import Session
from sqlalchemy_utils import drop_database, create_database
from typing import Literal

from utils import config
from db.populate.main import default_data, test_set_data
from db.session import Base
from models.Users import Users


def init_db(
    db: Session,
    *,
    db_script: str,
    show_data: bool = False,
    reset_db: bool | Literal["initial", "test_set"] = False,
    initial_data: list = default_data,
):
    """Initialize the database with default data

    Args:
        db (Session): The database session
        show_data (bool, optional): Whether to show the data in the terminal. Defaults to False.
        reset_db (bool | Literal["initial", "test_set"], optional):
            If False, the database will not be reset.
            If "initial", the database will be reset with minimum default data.
            If "test_set", the database will be reset with test fields for all tables alongside "initial" default data.
            If True, requires initial_data to be provided.
        initial_data (list, optional): The initial data to populate the database with, should be paired with reset_db=True."""

    print("\nInitializing database...")
    if reset_db == True and not initial_data:
        raise ValueError("initial_data must be provided if reset_db=True")

    engine = db.get_bind()
    if reset_db != False:
        if db_script == config.DB_SCRIPT_SQLITE:
            Base.metadata.drop_all(bind=engine)
        else:
            drop_database(engine.url)
            create_database(engine.url)
    Base.metadata.create_all(bind=engine)

    if reset_db == "initial":
        initial_data = default_data
    elif reset_db == "test_set":
        initial_data = test_set_data

    if db.query(Users).count() == 0:
        if show_data:
            print("\t=== Initializing database with default data... ===\n")
        for table in initial_data:
            db.add_all(table)
            db.commit()

    if show_data:
        print("Database initialized with the following data: ")
        for table in initial_data:
            print(table)
