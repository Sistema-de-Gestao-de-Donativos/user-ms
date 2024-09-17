from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests
from google.oauth2 import id_token

from ..api.users import controller, models

GOOGLE_CLIENT_ID = "your-google-client-id"  # TODO change this


def login(form_data: OAuth2PasswordRequestForm = Depends()) -> models.UserDAO:
    try:
        id_info = id_token.verify_oauth2_token(
            form_data.password, requests.Request(), GOOGLE_CLIENT_ID
        )

        user = controller.get_user_by_email(id_info["email"])

        return user
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
