from copy import deepcopy
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
from sqlalchemy.orm import Session
from typing import Literal, Optional

from auth.env import get_jwt_env
from db.session import get_db
from models.Users import Users
from schemas.Access_Logs import ACCESS_TOKEN_EXPIRE_MINUTES_DEFAULT, REFRESH_TOKEN_EXPIRE_MINUTES_DEFAULT
from schemas.Permissions import UserRole
from schemas.Users import UserStatus


# Configure the OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(
    data: dict,
    token_type: Literal["access", "refresh"],
    expiration: Optional[timedelta] | datetime = None,
):
    """
    Function to create a JWT token.

    Args:
        data (dict): Data to be encoded in the token.
        token_type (Literal["access", "refresh"]): Type of token to create.
        expiration (Optional[timedelta] | datetime):
            If timedelta, how long in the future the token will expire.
            If datetime, the exact time the token will expire.
            If None, the default expiration time will be used.
    """
    to_encode = deepcopy(data)

    if not expiration:
        token_default_expire = {
            "access": ACCESS_TOKEN_EXPIRE_MINUTES_DEFAULT,
            "refresh": REFRESH_TOKEN_EXPIRE_MINUTES_DEFAULT,
        }
        expiration_minutes = token_default_expire[token_type]
        expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
    elif isinstance(expiration, timedelta):
        expiration = datetime.utcnow() + expiration

    to_encode.update({
        "exp": expiration,
        "typ": f"{token_type}_token",
    })

    jwt_env = get_jwt_env()
    SECRET_KEY, ALGORITHM = jwt_env.get("JWT Secret"), jwt_env.get("Algorithm")

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_data_from_token(
    token: str = Depends(oauth2_scheme),
    token_type: Literal["access", "refresh"] = "access",
    can_be_expired: bool = False,
):
    jwt_env = get_jwt_env()
    SECRET_KEY, ALGORITHM = jwt_env.get("JWT Secret"), jwt_env.get("Algorithm")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token,
                             SECRET_KEY,
                             algorithms=[ALGORITHM],
                             options={"verify_exp": not can_be_expired})

        token_typ = payload.get("typ")
        if token_typ != f"{token_type}_token":
            raise credentials_exception

        if token_type == "refresh":
            jti = payload.get("jti")
            if jti is None:
                raise credentials_exception

        if token_type == "access":
            user_email = payload.get("sub")
            if user_email is None:
                raise credentials_exception

    except JWTError as jwt_error:
        raise credentials_exception from jwt_error

    return payload


def get_user_from_token(token: dict = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Function to get and validate the user token.

    Args:
        token (str): User token.
        db (Session): Database session.

    Raises:
        HTTPException UNAUTHORIZED: If the user token is invalid.

    Returns: Users: User information.
    """

    token_data = get_data_from_token(token)

    user_email = token_data.get("sub")
    if user_email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token"
        )

    return user_in_db(user_email, db)


def superadmin_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """This function receives a token, validates the user type and returns the body of the token."""
    validate_user(token, UserRole.superadmin, db)
    return get_data_from_token(token)


def admin_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """This function receives a token, validates the user type and returns the body of the token."""
    validate_user(token, UserRole.administrator, db)
    return get_data_from_token(token)


def developer_host_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """This function receives a token, validates the user type and returns the body of the token."""
    validate_user(token, UserRole.developer_host, db)
    return get_data_from_token(token)


def developer_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """This function receives a token, validates the user type and returns the body of the token."""
    validate_user(token, UserRole.developer, db)
    return get_data_from_token(token)


def user_in_db(email: str, db: Session = Depends(get_db)):
    """
    Function to get the user from the database.

    Args:
        email (str): Email of the user.
        db (Session): Database session.

    Returns:
        bool: True if the user is valid

    Raises:
        HTTPException NOT_FOUND: If user does not exist
    """

    user = db.query(Users).filter(Users.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your user doesnt exist. Contact the administrator if you believe this to be a mistake.")

    return user


def validate_user(token: str, user_desired_role: UserRole, db: Session = Depends(get_db)):
    """
    Function to check if the user can access the ication.

    Args:
        token (str): Token of the user.
        user_desired_role (UserRole): Type of user to check.
        db (Session): Database session.

    Raises:
        HTTPException UNAUTHORIZED: If the token is invalid
        HTTPException UNAUTHORIZED: If user does not have permission
        HTTPException FORBIDDEN: If user is not granted access to the ication
    """

    user = get_user_from_token(token, db)

    if user.status == UserStatus.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Your user is not accessible. Contact the administrator if you believe this to be a mistake.")

    if user.status == UserStatus.incomplete:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail="You must complete your registration before you can access this service.")

    if user.permission_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User permission not found. Contact an administrator if you believe this to be a mistake."
        )

    db_permission = None # TODO i had to delete this to make the code work (turani para ramiro)
    if db_permission is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="User permission not found. Contact the administrator if you believe this to be a mistake.")
    user_current_role = db_permission.type

    roles = [UserRole.superadmin, UserRole.administrator,
             UserRole.developer_host, UserRole.developer]
    current_desired_role_access_map = {
        UserRole.superadmin: roles,
        UserRole.administrator: roles[1:],
        UserRole.developer_host: roles[2:],
        UserRole.developer: roles[3:],
    }

    if user_desired_role not in current_desired_role_access_map[user_current_role]:
        raise HTTPException(
            status_code=401, detail="You do not have permission to do this.")
