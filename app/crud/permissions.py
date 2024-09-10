from typing import Annotated
from sqlalchemy.orm import Session

from models.Permissions import Permissions as PermissionsModel
from models.Users import Users as UsersModel
from schemas.Permissions import PermissionsCreate, PermissionsTyping, PermissionsUpdate
from schemas.Users import UsersTyping


def create_permission(db: Session, permission: PermissionsCreate) -> PermissionsModel:
    """Create a new permission in the database"""

    db_permission = PermissionsModel(
        max_concurrent_gpus=permission.max_concurrent_gpus,
        type=permission.type,
    )

    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)

    return db_permission


def get_permission(db: Session, permission_id: PermissionsTyping.id) -> PermissionsModel:
    """Get a permission from the database"""

    db_permission = db.query(PermissionsModel)\
        .join(UsersModel, UsersModel.permission_id == PermissionsModel.id)\
        .filter(UsersModel.permission_id == permission_id)

    permission = db_permission.first()

    return permission


def get_permission_by_user_id(db: Session, user_id: UsersTyping.id) -> PermissionsModel:
    """Get a permission from the database by user ID"""

    db_permission = db.query(PermissionsModel)\
        .join(UsersModel, UsersModel.permission_id == PermissionsModel.id)\
        .filter(UsersModel.id == user_id)

    permission = db_permission.first()

    return permission


def are_valid_permissions(db: Session, permission_ids: PermissionsTyping.permission_ids) -> Annotated[bool, "Check if all permissions exist in the database"]:
    """Test if permissions exist in the database"""

    db_permissions_size = db\
        .query(PermissionsModel)\
        .filter(PermissionsModel.id.in_(permission_ids))\
        .count()

    return db_permissions_size == len(permission_ids)


def update_permission(db: Session, permission_id: PermissionsTyping.id, permission: PermissionsUpdate) -> bool:
    """Update a permission in the database"""

    db_permission = db\
        .query(PermissionsModel)\
        .filter(PermissionsModel.id == permission_id)\

    updated = db_permission.update(permission)
    db.commit()

    return bool(updated)


def delete_permission(db: Session, permission_id: PermissionsTyping.id) -> bool:
    """Delete a permission from the database"""

    db_permission = db\
        .query(PermissionsModel)\
        .filter(PermissionsModel.id == permission_id)\

    deleted = db_permission.delete()
    db.commit()

    return bool(deleted)
