from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from typing import Annotated

from app.auth.hasher import hash_password
from app.auth.regex import email_invalid, password_invalid, password_regex_description
from app.auth.token import admin_token, get_user_from_token
from app.db.session import Database
from app.schemas.GPUs import GPUStatus
from app.schemas.Permissions import PermissionsCreate, UserRole
from app.schemas.Users import UsersInDb, UserStatus, UsersCreate, UsersDisplay, UsersOut, UsersUpdate, users_validators
from app.schemas.Validators import Typing
from app.utils.api import ApiResponse, ApiResponseList
import app.api.endpoints.administrator.permissions as permissions
import app.crud.gpu_pools as db_gpu_pools
import app.crud.gpu_sessions as db_gpu_sessions
import app.crud.gpus as db_gpus
import app.crud.permissions as db_permissions
import app.crud.users as db_users
import app.utils.conversions as convert

# Create a router instance to define the routes in this class
router = APIRouter(dependencies=[Depends(admin_token)])


@router.post("", response_model=ApiResponse[int])
def add_user(
    db: Database,
    user: Annotated[UsersCreate, Body(
        title="User information")],
):
    """### Add a user to the database

    ### Raises:
        - HTTPException BAD_REQUEST:
            - If the name is null
            - If the email is null
            - If the password is null"""

    user.name = user.name.strip()
    if not user.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name must be provided"
        )

    user.email = convert.case_insensitive(user.email)
    if email_invalid(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be a valid email address"
        )

    if password_invalid(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_regex_description
        )

    db_user = db_users.get_user_by_email(db, user.email)
    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    db_user = db_users.create_user(db, user)

    return ApiResponse[int](
        message=f"User {db_user.email} added successfully",
        data=db_user.id,
        status_code=status.HTTP_201_CREATED,
    )


@router.get("", response_model=ApiResponseList[UsersOut | UsersDisplay])
def get_users(
    db: Database,
    skip: Typing.skip = None,
    limit: Typing.limit = None,
    name: Annotated[str, Query(**users_validators.base_string,
                               description="Matches if any user's name contains the given string")] = None,
    email: Annotated[str, Query(**users_validators.base_string,
                                description="Matches if any user's email contains the given string")] = None,
    role: Annotated[UserRole, Query(
        description="The role of the users")] = None,
    min_current_active_sessions: Annotated[int, Query(**users_validators.non_negative,
                                                      description="The minimum number of active sessions the user must have")] = None,
    min_current_active_gpus: Annotated[int, Query(**users_validators.non_negative,
                                                  description="The minimum number of active GPUs the user must have")] = None,
    gpu_pool_id: Annotated[int, Query(**users_validators.positive,
                                      description="The ID of the GPU pool to get the users from")] = None,
    show_details: Annotated[bool, Query(
        description="Whether to return all fields or just partial information.",
    )] = False,
):
    """### Get all users from the database"""

    total_users, users = db_users.get_users(
        db,
        skip=skip,
        limit=limit,
        name=name,
        email=email,
        role=role,
        min_current_active_sessions=min_current_active_sessions,
        min_current_active_gpus=min_current_active_gpus,
        gpu_pool_id=gpu_pool_id,
    )

    if not show_details:
        users_display = []
        for user in users:
            user_permission = db_permissions.get_permission(
                db, user.permission_id)
            user_role = getattr(user_permission, 'type', UserRole.undefined)
            max_concurrent_gpus = getattr(
                user_permission, 'max_concurrent_gpus', 0)
            pool_count, _ = db_gpu_pools.get_gpu_pools(db, user_id=user.id)
            session_count, _ = db_gpu_sessions.get_gpu_sessions(
                db, user_id=user.id)
            user_display = UsersDisplay(
                id=user.id,
                name=user.name,
                email=user.email,
                pool_count=pool_count,
                role=user_role,
                session_count=session_count,
                max_concurrent_gpus=max_concurrent_gpus,
                status=user.status,
            )
            users_display.append(user_display)
        users = users_display

    return ApiResponseList(
        message="Users retrieved successfully",
        data={
            "total_count": total_users,
            "filtered_list": users,
        }
    )


@router.get("/{user_id}", response_model=ApiResponse[UsersOut])
def get_user(
    db: Database,
    user_id: Annotated[int, Path(**users_validators.positive,
                                 description="The ID of the user to retrieve")]
):
    """### Get a user from the database

    ### Raises:
        - NOT_FOUND: If the user does not exist"""

    db_user = db_users.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ApiResponse(
        message="User retrieved successfully",
        data=db_user,
    )


@router.get("/email/{email}", response_model=ApiResponse[UsersOut])
def get_user_by_email(
    db: Database,
    email: Annotated[str, Path(**users_validators.email,
                               description="The email of the user to retrieve")],
):
    """### Get a user from the database by email

    ### Raises:
        - NOT_FOUND: If the user does not exist"""

    email = convert.case_insensitive(email)
    if email_invalid(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be a valid email address"
        )

    db_user = db_users.get_user_by_email(db, email)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ApiResponse(
        message=f"User {email} retrieved successfully",
        data=db_user,
    )


@router.put("/{user_id}", response_model=ApiResponse[int])
def update_user(
    db: Database,
    user_id: Annotated[int, Path(**users_validators.positive,
                                 description="The ID of the user to update")],
    user: Annotated[UsersUpdate, Body(
        title="User information")],
    admin: Annotated[UsersInDb, Depends(get_user_from_token)],
):
    """### Update a user in the database

    ### Raises:
        - BAD_REQUEST: If no fields are provided to update"""

    updated_user = {}

    skip_fields = ["email"]
    for key, value in user:
        if key not in skip_fields and value is not None:
            updated_user[key] = value

    if user.email is not None:
        if email_invalid(user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email must be a valid email address"
            )
        updated_user["email"] = user.email

    db_user = db_users.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if db_user.status == UserStatus.active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is currently active and cannot be updated. Please, stop all GPU Sessions first."
        )

    admin_permission = db_permissions.get_permission(db, admin.permission_id)
    admin_user = [UserRole.superadmin, UserRole.administrator]
    can_edit_user = admin.permission_id == db_user.permission_id or \
        admin_permission.type == UserRole.superadmin or \
        (db_user.permission.type not in admin_user)
    if not can_edit_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrators cannot update other administrators"
        )

    if "status" in updated_user:
        if updated_user["status"] == UserStatus.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User status cannot be set to active. Please, start a GPU Session first."
            )

        _, db_host_gpus = db_gpus.get_gpus(db, user_id=db_user.id)
        gpus_ids = [gpu.id for gpu in db_host_gpus]

        are_gpus_available = db_gpus.are_gpus_available(db, gpus_ids,
                                                        gpu_status=[GPUStatus.host_offline, GPUStatus.disabled, GPUStatus.idle])
        if not are_gpus_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot update a User while they are in a session. Please stop all GPU Sessions first")

        updated_user["status"] = user.status

    if len(updated_user) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    updated = db_users.update_user(db, user_id, updated_user)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ApiResponse[int](
        message=f"User updated successfully",
        data=user_id,
    )


@router.patch("/{user_id}", response_model=ApiResponse[int])
def update_user_password(
    db: Database,
    user_id: Annotated[int, Path(**users_validators.positive,
                                 description="The ID of the user to update")],
    password: Annotated[str, Body(
        **users_validators.password,
        description="The new password for the user")],
    admin: Annotated[UsersInDb, Depends(get_user_from_token)],
):
    """### Update a user's password in the database

    ### Raises:
        - BAD_REQUEST: If the password is null"""

    if password_invalid(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_regex_description
        )

    db_user = db_users.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    admin_permission = db_permissions.get_permission(db, admin.permission_id)
    admin_user = [UserRole.superadmin, UserRole.administrator]
    can_edit_user = admin.permission_id == db_user.permission_id or \
        admin_permission.type == UserRole.superadmin or \
        (db_user.permission.type not in admin_user)
    if not can_edit_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrators cannot update other administrators"
        )

    updated = db_users.update_user(db, user_id, {
        "hashed_password": hash_password(password)
    })

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ApiResponse[int](
        message="User's password updated successfully",
        data=user_id,
    )


@router.delete("/{user_id}", response_model=ApiResponse[int])
def remove_user(
    db: Database,
    user_id: Annotated[int, Path(**users_validators.positive,
                                 description="The ID of the user to remove")],
    admin: Annotated[UsersInDb, Depends(get_user_from_token)],
):
    """### Remove a user from the database

    ### Raises:
        - NOT_FOUND: If the user does not exist"""

    db_user = db_users.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_has_permission = db_user.permission_id is not None
    if user_has_permission:
        user_permission = db_permissions.get_permission(
            db, db_user.permission_id)
        user_has_permission = user_permission is not None

    admin_permission = db_permissions.get_permission(db, admin.permission_id)
    admin_user = [UserRole.superadmin, UserRole.administrator]
    can_delete_user = admin.permission_id == db_user.permission_id \
        or admin_permission.type == UserRole.superadmin \
        or not user_has_permission \
        or user_permission.type not in admin_user
    if not can_delete_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrators cannot delete other administrators"
        )

    if user_has_permission:
        try:
            permissions.delete_permission(db_user.permission_id, db)
        except:
            # Ignore any error that may occur when deleting the permission via the API
            pass
    deleted = db_users.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    return ApiResponse[int](
        message=f"User deleted successfully",
        data=user_id,
    )
