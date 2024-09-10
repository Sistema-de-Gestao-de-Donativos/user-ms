from sqlalchemy.orm import Session
from typing import Optional

from models.Access_Logs import AccessLogs as AccessLogsModel


def insert_row(db: Session, token: str, id: Optional[int] = None) -> AccessLogsModel:
    """Insert a new row into the access_logs table"""

    db_access_logs = AccessLogsModel(id=id, token=token)

    db.add(db_access_logs)
    db.commit()
    db.refresh(db_access_logs)

    return db_access_logs


def get_row(db: Session, id: int) -> AccessLogsModel:
    """Get a row from the access_logs table"""

    return db.get(AccessLogsModel, id)


def get_row_by_token(db: Session, token: str) -> AccessLogsModel:
    """Get a row from the access_logs table"""

    db_access_logs = db\
        .query(AccessLogsModel)\
        .filter(AccessLogsModel.token == token)\

    access_logs = db_access_logs.first()

    return access_logs


def delete_row(db: Session, id: str) -> None:
    """Delete a row from the access_logs table"""

    db_access_logs = db\
        .query(AccessLogsModel)\
        .filter(AccessLogsModel.id == id)\

    deleted = db_access_logs.delete()
    db.commit()

    return bool(deleted)
