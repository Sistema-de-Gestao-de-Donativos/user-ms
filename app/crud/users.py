from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Annotated

from models.Permissions import Permissions as PermissionsModel
from models.Users import Users as UsersModel
from schemas.Users import UsersCreate, UsersTyping, UsersUpdate
from auth.hasher import hash_password
from schemas.Validators import Typing
import utils.conversions as convert


def create_user(db: Session, user: UsersCreate) -> UsersModel:
    """Create a new user in the database"""

    db_user = UsersModel(
        name=user.name,
        email=user.email,
        status=user.status,
        hashed_password=hash_password(user.password),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_users(
    db: Session,
    skip: Typing.skip = 0,
    limit: Typing.limit = 100,
    name: UsersTyping.name = None,
    email: Annotated[UsersTyping.name,
                     "Since this can be a partial email, such as @lis, for example, follows the same rules as a name instead of .email"] = None,
    role: UsersTyping.role = None,
    min_current_active_sessions: Typing.non_negative = None,
    min_current_active_gpus: Typing.non_negative = None,
    invert_filters: bool = False,
) -> tuple[int, list[UsersModel]]:
    """Get all users from the database"""

    db_users = db.query(UsersModel)
    if name is not None:
        name = convert.case_insensitive(name)
        if not invert_filters:
            db_users = db_users.filter(UsersModel.name.contains(name))
        else:
            db_users = db_users.filter(~UsersModel.name.contains(name))

    if email is not None:
        email = convert.case_insensitive(email)
        if not invert_filters:
            db_users = db_users.filter(UsersModel.email.contains(email))
        else:
            db_users = db_users.filter(~UsersModel.email.contains(email))

    total_users = db_users.count()

    users = db_users\
        .offset(skip)\
        .limit(limit)\
        .all()

    return total_users, users


def get_user(db: Session, user_id: UsersTyping.id) -> UsersModel:
    """Get a user from the database by ID"""

    return db.get(UsersModel, user_id)


def get_user_by_email(db: Session, email: UsersTyping.email) -> UsersModel:
    """Get a user from the database by email"""

    email = convert.case_insensitive(email)
    db_user = db\
        .query(UsersModel)\
        .filter(UsersModel.email == email)

    user = db_user.first()

    return user


def get_user_by_permission_id(db: Session, permission_id: int):
    """
    Get a user from the database by permission ID

    Args:
        db (Session): The database session
        permission_id (int): The ID of the permission of the user to get

    Returns:
        Users: The user
    """

    db_user = db\
        .query(UsersModel)\
        .filter(UsersModel.permission_id == permission_id)

    user = db_user.first()

    return user


def update_user(db: Session, user_id: UsersTyping.id, user: UsersUpdate) -> bool:
    """Update a user in the database"""

    db_user = db\
        .query(UsersModel)\
        .filter(UsersModel.id == user_id)\

    updated = db_user.update(user)
    db.commit()

    return bool(updated)


def add_permission(db: Session, user_id: UsersTyping.id, permission_id: Typing.id) -> bool:
    """Add a permission to a user"""

    db_user = db\
        .query(UsersModel)\
        .filter(UsersModel.id == user_id)\

    updated = db_user.update({"permission_id": permission_id})
    db.commit()

    return bool(updated)


def remove_permission(db: Session, user_id: UsersTyping.id) -> bool:
    """Remove a permission from a user"""

    db_user = db\
        .query(UsersModel)\
        .filter(UsersModel.id == user_id)\

    updated = db_user.update({"permission_id": None})
    db.commit()

    return bool(updated)


def delete_user(db: Session, user_id: UsersTyping.id) -> bool:
    """Delete a user from the database"""

    db_user = db\
        .query(UsersModel)\
        .filter(UsersModel.id == user_id)\

    deleted = db_user.delete()
    db.commit()

    return bool(deleted)
