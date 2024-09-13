from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from google.oauth2 import id_token
from google.auth.transport import requests

from ....db.users import models
from .. import controller

auth_router = APIRouter()

GOOGLE_CLIENT_ID = "your-google-client-id" #TODO change this

async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> models.User :
    try:
        id_info = id_token.verify_oauth2_token(form_data.password, requests.Request(), GOOGLE_CLIENT_ID)

        user = await controller.get_user_by_email(id_info['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
