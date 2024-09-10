from enum import Enum


ACCESS_TOKEN_EXPIRE_MINUTES_DEFAULT = 60 * 12  # 12 hours
REFRESH_TOKEN_EXPIRE_MINUTES_DEFAULT = 60 * 24 * 7  # 7 days


class AccessLogsIssuer(Enum):
    # Invited by the administrator
    email_invite = "email_invite"
    # Clicked on the "forgot password" link
    forgot_password = "forgot_password"


class AccessLogs():
    id: int
    token: str
