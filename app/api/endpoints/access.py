from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status

from auth.hasher import hash_password, verify_password
from auth.regex import email_invalid, password_invalid, password_regex_description
from auth.token import admin_token, create_jwt_token, developer_token, get_user_from_token
from db.session import Database
from models.Users import Users
from schemas.Access_Logs import AccessLogsIssuer
from schemas.Permissions import PermissionsCreate
from schemas.Users import UserStatus, UsersCreate, UsersInvite, UsersTyping, users_validators
from utils.api import ApiResponse
from utils.email import send_custom_email, send_welcome_html_email, FORGOT_PASSWORD_URL
import api.endpoints.administrator.permissions as permissions
import crud.access_logs as db_access_logs
import crud.users as db_users
import utils.conversions as convert

# Create a router instance to define the routes in this class
router = APIRouter()


password_example = UsersTyping().get_field("password", "examples")
email_example = UsersTyping().get_field("email", "examples")


@router.post("/email_invite", dependencies=[Depends(admin_token)], response_model=ApiResponse[UsersTyping.email_invite_api_response])
def invite_user(
    db: Database,
    users_info: Annotated[UsersInvite, Body(...,
                                            description="The information of the users to invite")],
):
    """### Invites a user to the application, creating a default incomplete user which will be completed when the user accepts the invitation

    ### Raises:
        - BAD_REQUEST:
            - If no users are provided
            - If the link expiration is less than 1 day
            - If the link expiration is more than 1 year (366 days)
            - If the default password is invalid"""

    if not users_info.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify at least one user"
        )

    if users_info.link_expiration_days < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link expiration must be at least 1 day"
        )

    MAX_LINK_EXPIRATION_DAYS = 366
    if users_info.link_expiration_days > MAX_LINK_EXPIRATION_DAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Link cannot stay active for more than a year ({MAX_LINK_EXPIRATION_DAYS} days)"
        )

    if password_invalid(users_info.default_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_regex_description
        )

    replaceable_email_attributes = ["name", "email"]

    invalid_emails = []
    for user in users_info.users:
        email = getattr(user, 'email', '') or user['email']
        email = convert.case_insensitive(email)

        if email_invalid(email):
            invalid_emails.append((400, email))
            continue

        db_user = db_users.get_user_by_email(db, email)
        if db_user is not None:
            invalid_emails.append((409, email))
            continue

        name = getattr(user, 'name', '') or user['name']
        new_user = UsersCreate(
            name=name,
            email=email,
            password=users_info.default_password,
            status=UserStatus.incomplete,
        )
        db_user = db_users.create_user(db, new_user)

        issue_time = datetime.now()
        expire_time = timedelta(days=users_info.link_expiration_days)
        reset_password_data = {
            "iat": issue_time,
            "iss": AccessLogsIssuer.email_invite.value,
            "sub": email,
            "exp": issue_time + expire_time
        }
        reset_token = create_jwt_token(reset_password_data,
                                       token_type="access",
                                       expiration=expire_time)
        db_access_logs.insert_row(db, reset_token)

        permission = PermissionsCreate(
            user_id=db_user.id,
            type=users_info.permissions.type,
            max_concurrent_gpus=users_info.permissions.max_concurrent_gpus,
            gpu_pools_permissions=users_info.permissions.gpu_pools_permissions
        )
        permissions.add_permission(db, permission)

        email_subject = users_info.subject
        email_body = users_info.body
        for attribute in replaceable_email_attributes:
            if not hasattr(user, attribute):
                continue
            field = "{{" + attribute + "}}"
            email_subject = email_subject.replace(
                field, getattr(user, attribute))
            email_body = email_body.replace(field, getattr(user, attribute))

        sent = send_welcome_html_email(
            email, email_subject, email_body, reset_token)
        if not sent:
            invalid_emails.append((503, email))

    total_invites = len(users_info.users)
    successful_invites = total_invites - len(invalid_emails)

    success = successful_invites == total_invites
    status_code = status.HTTP_200_OK if success else status.HTTP_206_PARTIAL_CONTENT

    return ApiResponse(
        message=f"{successful_invites} of {total_invites} users invited successfully",
        data=invalid_emails,
        status_code=status_code,
        success=success,
    )


@router.patch("/email_invite/{reset_token}", response_model=ApiResponse[int])
def complete_invite_user(
    db: Database,
    reset_token: Annotated[str, Path(description="The token received via the link from the invitation email")],
    email: Annotated[str, Body(**users_validators.email, examples=[email_example],
                               description="The email of the user to complete the invitation")],
    name: Annotated[str, Body(**users_validators.base_string, examples=[UsersTyping().get_field("name", "examples")],
                              description="The name of the user to complete the invitation")],
    password: Annotated[str, Body(**users_validators.password, examples=[password_example],
                                  description="The password of the user to complete the invitation")],
):
    """### Completes the invitation of a user to the application

    ### Raises:
        - BAD_REQUEST:
            - If the name is not provided
            - If the password is invalid
            - If the reset token is invalid
        - NOT_FOUND: If the user does not exist"""

    user = db_users.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    reset_code = db_access_logs.get_row_by_token(db, reset_token)
    reset_token = getattr(reset_code, "token", None)
    if not reset_code or not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset code"
        )

    reset_code_user = get_user_from_token(reset_token, db)
    if reset_code_user.email != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset code"
        )

    if not convert.case_insensitive(name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name must be provided"
        )

    if password_invalid(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_regex_description
        )

    updated_user = {
        "name": name,
        "hashed_password": hash_password(password),
        "status": UserStatus.enabled,
    }

    updated = db_users.update_user(db, user.id, updated_user)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_access_logs.delete_row(db, reset_token)

    return ApiResponse[int](
        message="User completed successfully",
        data=user.id,
    )


@router.post("/forgot_password", response_model=ApiResponse[None])
def forgot_password(
    db: Database,
    user_email: Annotated[str, Body(**users_validators.email, examples=[email_example],
                                    description="The email of the user to send the reset password email")],
):
    """### Sends a reset password email to the user

    ### Raises:
        - BAD_REQUEST: If the email is invalid
        - NOT_FOUND: If the user does not exist
        - FORBIDDEN: If the user is disabled"""

    user_email = convert.case_insensitive(user_email)
    if email_invalid(user_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be a valid email address"
        )

    db_user = db_users.get_user_by_email(db, user_email)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if db_user.status == UserStatus.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this service. Contact an administrator for more information."
        )

    updated = db_users.update_user(
        db, db_user.id, {"status": UserStatus.incomplete})
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not reset user password"
        )

    issue_time = datetime.now()
    expire_time = timedelta(minutes=60)
    reset_password_data = {
        "iat": issue_time,
        "iss": AccessLogsIssuer.forgot_password.value,
        "sub": user_email,
        "exp": issue_time + expire_time
    }
    reset_token = create_jwt_token(reset_password_data,
                                   token_type="access",
                                   expiration=expire_time)
    db_access_logs.insert_row(db, reset_token)

    reset_password_url = f"{FORGOT_PASSWORD_URL}?e={user_email}&t={reset_token}"
    sent = send_custom_email(user_email, "Password Reset - Mithra",
                             f"Click the following link to reset your password: {reset_password_url}. It will expire in 1 hour.")

    if not sent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not send email to {user_email}"
        )

    return ApiResponse[None](
        message=f"Reset password email sent to {user_email}",
    )


@router.patch("/forgot_password/{reset_token}", response_model=ApiResponse[None])
def reset_password(
    db: Database,
    reset_token: Annotated[str, Path(description="The reset token received in the forgot password email")],
    email: Annotated[str, Body(**users_validators.email, examples=[email_example],
                               description="The email of the user to reset the password")],
    new_password: Annotated[str, Body(**users_validators.password, examples=[password_example],
                                      description="The new password for the user")],
):
    """### Resets the password of a user

    ### Raises:
        - BAD_REQUEST:
            - If the email is invalid
            - If the password is invalid
            - If the reset token is invalid
        - NOT_FOUND: If the user does not exist"""

    user_email = convert.case_insensitive(email)
    if email_invalid(user_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be a valid email address"
        )

    db_user = db_users.get_user_by_email(db, user_email)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    reset_code = db_access_logs.get_row_by_token(db, reset_token)
    reset_token = getattr(reset_code, "token", None)
    if not reset_code or not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset code"
        )

    reset_code_user = get_user_from_token(reset_token, db)
    if reset_code_user.email != user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset code"
        )

    if password_invalid(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_regex_description
        )

    updated = db_users.update_user(db, db_user.id, {
        "hashed_password": hash_password(new_password),
        "status": UserStatus.enabled,
    })
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_access_logs.delete_row(db, reset_token)

    return ApiResponse[None](
        message=f"Password reset for {user_email} successfully",
    )


@router.patch("/change_password", dependencies=[Depends(developer_token)], response_model=ApiResponse[None])
def change_password(
    db: Database,
    old_password: Annotated[str, Body(**users_validators.password, examples=[password_example],
                                      description="The old password of the user")],
    new_password: Annotated[str, Body(**users_validators.password, examples=[f"{password_example}2"],
                                      description="The new password of the user")],
    user: Users = Depends(get_user_from_token),
):
    """### Changes the password of the user

    ### Raises:
        - BAD_REQUEST:
            - If the new password is the same as the old password
            - If the new password is invalid
        - UNAUTHORIZED: If the old password is incorrect"""

    if old_password == new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the old password"
        )

    if password_invalid(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_regex_description
        )

    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect"
        )

    updated = db_users.update_user(db, user.id, {
        "hashed_password": hash_password(new_password)
    })
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not change user password"
        )

    return ApiResponse[None](
        message="Password changed successfully",
    )
