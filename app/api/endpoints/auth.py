from datetime import timedelta
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from auth.env import get_jwt_env
from auth.hasher import verify_password
from auth.token import create_jwt_token, get_data_from_token
from db.session import Database
from models.Users import Users
from schemas.Auth import AuthTyping, LoginResponse, TokenResponse
from schemas.Users import UserStatus, UsersBaseInfo
from utils.api import ApiResponse
import utils.conversions as convert
import crud.access_logs as db_access_logs

# Create a router instance to define the routes in this class
router = APIRouter()


PERMISSION_ERROR = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                 detail="You do not have permission to access this service. Please contact an administrator if you believe this is an error.")


@router.post("/token", name="Login", response_model=LoginResponse)
def token_login(db: Database, form_data: OAuth2PasswordRequestForm = Depends()):
    """### Function to login and get the authentication token.

    ### Args:
        - form_data (OAuth2PasswordRequestForm): The form data containing the username (email) and password.

    ### Raises:
        - HTTPException BAD_REQUEST: If the username or password is incorrect.
        - HTTPException FORBIDDEN: If the user is not granted access to the ication."""

    email = convert.case_insensitive(form_data.username)

    db_user = db.query(Users).filter(Users.email == email).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    if db_user.status == UserStatus.disabled:
        raise PERMISSION_ERROR

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    jwt_env = get_jwt_env()
    ACCESS_TOKEN_EXPIRE_MINUTES = jwt_env.get("Access Token Expire Minutes")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {"sub": email}
    access_token = create_jwt_token(access_token_data,
                                    token_type="access",
                                    expiration=access_token_expires)
    access_token_log = db_access_logs.insert_row(db, access_token)
    access_token_id = str(access_token_log.id)

    REFRESH_TOKEN_EXPIRE_MINUTES = jwt_env.get("Refresh Token Expire Minutes")
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token_data = {"jti": access_token_id}
    refresh_token = create_jwt_token(refresh_token_data,
                                     token_type="refresh",
                                     expiration=refresh_token_expires)

    return LoginResponse(
        info=UsersBaseInfo(
            name=db_user.name,
        ),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.put("/refresh_token", name="Refresh Token", response_model=ApiResponse[TokenResponse])
def refresh_token_login(db: Database,
                        refresh_token: Annotated[str, Body(..., examples=[AuthTyping().get_field("refresh_token", "examples")],
                                                           description="The refresh token used to refresh the authentication token. Returned from the login endpoint.")],
                        ):
    """### Function to refresh the authentication token"""

    refresh_token_data = get_data_from_token(
        refresh_token, token_type="refresh")

    token_target_id = refresh_token_data.get("jti")
    access_log = db_access_logs.get_row(db, token_target_id)
    if not access_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token target")

    access_token_data = get_data_from_token(
        access_log.token, can_be_expired=True)

    db_access_logs.delete_row(db, token_target_id)

    jwt_env = get_jwt_env()
    ACCESS_TOKEN_EXPIRE_MINUTES = jwt_env.get("Access Token Expire Minutes")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(access_token_data,
                                    token_type="access",
                                    expiration=access_token_expires)
    db_access_logs.insert_row(db, access_token, token_target_id)

    return ApiResponse[TokenResponse](
        message="Successfully refreshed token.",
        data={
            "access_token": access_token,
            "token_type": "bearer",
        },
    )
