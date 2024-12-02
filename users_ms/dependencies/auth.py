import jwt
from fastapi import Depends, FastAPI, Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase
from starlette.exceptions import HTTPException
from starlette.requests import Request

from ..settings import Settings

settings = Settings()


def init_app(app: FastAPI) -> None:
    """
    Initializes the authentication module for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        None
    """
    app.router.dependencies.append(Depends(validate_request))


def validate_request(
    request: Request,
    authorization: HTTPAuthorizationCredentials | None = Security(
        HTTPBase(scheme="bearer", auto_error=False)
    ),
):
    """
    Validates the incoming request.

    If the API key is the root key, the request is authorized.
    If the API key is a JWT token, it is validated and its permissions are checked.

    Returns:
        None

    Raises:
        HTTPException: If the request is not authorized.
    """
    if not authorization:
        d = {
            "loc": ["header", "Authorization"],
            "msg": "Missing Authorization header.",
            "type": "MissingHeader",
        }

        raise HTTPException(401, detail=str(d))

    if authorization.credentials == settings.API_SECRET:
        request.state.user = {"role": "superadmin"}
    else:
        # validate JWT token with public key
        try:
            decoded_token = jwt.decode(
                authorization.credentials, settings.JWT_PUBLIC_KEY, algorithms=["RS256"]
            )
            request.state.user = decoded_token
        except jwt.exceptions.DecodeError:
            d = {
                "loc": ["header", "Authorization"],
                "msg": "Invalid token.",
                "type": "InvalidToken",
            }
            raise HTTPException(401, detail=str(d))
        except jwt.exceptions.ExpiredSignatureError:
            d = {
                "loc": ["header", "Authorization"],
                "msg": "Token has expired.",
                "type": "ExpiredToken",
            }
            raise HTTPException(401, detail=str(d))
