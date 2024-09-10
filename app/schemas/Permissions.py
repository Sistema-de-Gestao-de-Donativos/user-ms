from enum import Enum
from pydantic import BaseModel, Field
from typing import Annotated, Optional

from schemas.Validators import Typing, Validators


SUPERADMIN_ID = 1
ADMIN_ID = 2
DEVELOPER_HOST_ID = 3
DEVELOPER_ID = 4


class UserRole(Enum):
    superadmin = "superadmin"
    administrator = "administrator"
    developer_host = "developer_host"
    developer = "developer"
    undefined = "permission_missing"


class PermissionsTyping(Typing):
    """Define the typing for the Permissions schema. It is used for the type hinting and the validation of the schema."""

    id = Typing().get_with_changed_description(
        "id", "permission", replace_entity=True)

    max_concurrent_gpus = Annotated[int, Field(1, **Validators.non_negative, examples=[1, 2],
                                               description="The maximum number of concurrent GPUs the user can use.")]

    type = Annotated[UserRole, Field(examples=[UserRole.developer, UserRole.superadmin],
                                     description="The user's role. It will affect the user's permissions and access to the system.")]

    gpu_pools_permissions = Annotated[list[int], Field([1], examples=[[1, 2], [3, 4]],
                                                       description="The list of GPU pools the user will be a part of.")]

    permission_ids = Typing().get_with_changed_description(
        "ids", "permissions", replace_entity=True)


class PermissionsBase(BaseModel):
    max_concurrent_gpus: PermissionsTyping.max_concurrent_gpus = 1
    type: PermissionsTyping.type = UserRole.developer
    gpu_pools_permissions: PermissionsTyping.gpu_pools_permissions = [1]


class PermissionsCreate(PermissionsBase):
    user_id: Typing.id
    pass


class PermissionsUpdate(PermissionsBase):
    max_concurrent_gpus: Optional[PermissionsTyping.max_concurrent_gpus] = None
    type: Optional[PermissionsTyping.type] = None
    gpu_pools_permissions: Optional[PermissionsTyping.gpu_pools_permissions] = None


class Permissions(PermissionsBase):
    id: PermissionsTyping.id # type: ignore

    class Config:
        from_attributes = True
