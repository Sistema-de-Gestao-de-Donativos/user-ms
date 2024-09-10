from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status

from db.session import Database
from schemas.Permissions import (
    SUPERADMIN_ID,
    PermissionsTyping,
    UserRole,
    Permissions,
    PermissionsCreate,
    PermissionsUpdate,
)
from schemas.Users import UsersInDb
from schemas.Validators import Typing, Validators
from utils.api import ApiResponse
from auth.token import admin_token, get_user_from_token
import crud.permissions as db_permissions
import crud.users as db_users


# Create a router instance to define the routes in this class
router = APIRouter(dependencies=[Depends(admin_token)])


permission_id_description = PermissionsTyping().get_field("id", "description")


@router.post("", response_model=ApiResponse[PermissionsTyping.id])
def add_permission(
    db: Database,
    permission: Annotated[PermissionsCreate, Body(
        title="User information")],
):
    """### Add a permission to the database

    ### Raises:
        - BAD_REQUEST:
            - If the permission type is superadmin
            - If the max concurrent GPUs is not a positive integer
            - If the user already has a permission"""

    if permission.type == UserRole.superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create superadmin permissions"
        )

    if permission.max_concurrent_gpus < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max concurrent GPUs must be a positive integer"
        )

    db_user = db_users.get_user(db, permission.user_id)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if db_user.permission_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a permission"
        )

    db_permission = db_permissions.create_permission(db, permission)

    db_users.add_permission(db, permission.user_id, db_permission.id)

    return ApiResponse[int](
        message="Permission added successfully",
        data=db_permission.id,
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/{permission_id}", response_model=ApiResponse[Permissions])
def get_permission(
    db: Database,
    permission_id: Annotated[int, Path(**Validators.positive,
                                       description=permission_id_description)],
):
    """### Get a permission from the database

    ### Raises:
        - NOT_FOUND: If the permission is not found"""

    db_permission = db_permissions.get_permission(db, permission_id)

    if db_permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    gpu_pools_permissions = None
    gpu_pools_ids = [
        gpu_pool_permission.id for gpu_pool_permission in gpu_pools_permissions]

    permission = Permissions(
        id=db_permission.id,
        type=db_permission.type,
        max_concurrent_gpus=db_permission.max_concurrent_gpus,
        gpu_pools_permissions=gpu_pools_ids
    )

    return ApiResponse(
        message=f"Permission retrieved successfully",
        data=permission
    )


@router.get("/user_id/{user_id}", response_model=ApiResponse[Permissions])
def get_permission_by_user_id(
    db: Database,
    user_id: Annotated[int, Path(**Validators.positive,
                                 description=Typing().get_field("id", "description").replace("entity", "user"))],
):
    """### Get a user's permission from the database

    ### Raises:
        - NOT_FOUND: If the user does not exist
        - BAD_REQUEST: If the user does not have a permission"""

    db_user = db_users.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if db_user.permission_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a permission"
        )

    db_permission = db_permissions.get_permission(
        db, db_user.permission_id)
    if db_permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    gpu_pools_permissions = None
    gpu_pools_permissions_ids = [
        gpu_pool_permission.id for gpu_pool_permission in gpu_pools_permissions]

    permission = Permissions(
        id=db_permission.id,
        max_concurrent_gpus=db_permission.max_concurrent_gpus,
        type=db_permission.type,
        gpu_pools_permissions=gpu_pools_permissions_ids,
    )

    return ApiResponse(
        message=f"Permission retrieved successfully",
        data=permission
    )


@router.put("/{permission_id}", response_model=ApiResponse[None])
def update_permission(
    db: Database,
    permission_id: Annotated[int, Path(**Validators.positive,
                                       description=permission_id_description)],
    permission: Annotated[PermissionsUpdate, Body(
        title="User information")],
    user: UsersInDb = Depends(get_user_from_token),
):
    """### Update a permission in the database

    ### Raises:
        - BAD_REQUEST:
            - If there are no fields to update
            - If the permission type is superadmin
        - NOT_FOUND: If the permission is not found"""

    db_user_permission = db_permissions.get_permission(db, user.permission_id)
    if db_user_permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User permission not found"
        )

    db_permission = db_permissions.get_permission(db, permission_id)
    if db_permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    if db_permission.type == UserRole.superadmin \
            and db_user_permission.type != UserRole.superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update superadmin permissions"
        )

    invalid_keys = ['gpu_pools_permissions']
    updated_permission = {}
    for key, value in permission:
        if key in invalid_keys:
            continue
        if value is not None:
            updated_permission[key] = value


    if len(updated_permission) > 0:
        if "type" in updated_permission \
                and updated_permission["type"] == UserRole.superadmin \
                and db_user_permission.type != UserRole.superadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update to superadmin permissions"
            )

        updated = db_permissions.update_permission(
            db, permission_id, updated_permission)

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

    return ApiResponse[None](
        message=f"Permission updated successfully"
    )


@router.delete("/{permission_id}", response_model=ApiResponse[PermissionsTyping.id])
def delete_permission(
    db: Database,
    permission_id: Annotated[int, Path(**Validators.positive,
                                       description=permission_id_description)],
):
    """### Delete a permission from the database

    ### Raises:
        - NOT_FOUND: If the permission is not found"""

    def validate_deleted(deleted: bool):
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

    if permission_id == SUPERADMIN_ID:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete superadmin permission"
        )

    db_permission = get_permission(db=db, permission_id=permission_id)
    db_permission = db_permission.data
    deleted = db_permissions.delete_permission(db, permission_id)
    validate_deleted(deleted)

    db_user = db_users.get_user_by_permission_id(db, permission_id)
    deleted = db_users.remove_permission(db, db_user.id)
    validate_deleted(deleted)

    return ApiResponse[int](
        message="Permission deleted successfully",
        data=permission_id,
    )
