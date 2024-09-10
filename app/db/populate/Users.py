from auth.hasher import hash_password
from models.Users import Users
from schemas.Permissions import (
    SUPERADMIN_ID,
    ADMIN_ID,
    DEVELOPER_HOST_ID,
    DEVELOPER_ID,
)


default_users = [
    Users(
        id=SUPERADMIN_ID,
        name="Super Admin",
        email="super_admin@pucrs.br",
        hashed_password=hash_password("superadmin"),
        permission_id=SUPERADMIN_ID,
    ),
    Users(
        id=ADMIN_ID,
        name="Admin",
        email="admin@pucrs.br",
        hashed_password=hash_password("admin"),
        permission_id=ADMIN_ID,
    ),
    Users(
        id=DEVELOPER_HOST_ID,
        name="Developer Host",
        email="developer_host@pucrs.br",
        hashed_password=hash_password("developerhost"),
        permission_id=DEVELOPER_HOST_ID,
    ),
    Users(
        id=DEVELOPER_ID,
        name="Developer",
        email="developer@pucrs.br",
        hashed_password=hash_password("developer"),
        permission_id=DEVELOPER_ID,
    ),
]

test_set_users = [
    Users(
        name="Vinicius Turani",
        email="v.turani@edu.pucrs.br",
        hashed_password=hash_password("vturani"),
        permission_id=5,
    ),
    Users(
        name="Felipe Freitas",
        email="felipe.freitas@pucrs.br",
        hashed_password=hash_password("felipefreitas"),
        permission_id=6,
    ),
    Users(
        name="Guilherme Romanini",
        email="guilherme.kuticoski@pucrs.br",
        hashed_password=hash_password("guilhermekuticoski"),
        permission_id=7,
    ),
    Users(
        name="João Bergallo",
        email="jbergallo@pucrs.br",
        hashed_password=hash_password("jbergallo"),
        permission_id=8,
    )
]

users = default_users + test_set_users
