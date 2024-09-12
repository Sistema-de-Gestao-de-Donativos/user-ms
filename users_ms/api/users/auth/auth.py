from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
import logging

auth_router = APIRouter()

GOOGLE_CLIENT_ID = "your-google-client-id"  # Replace with your actual Google client ID

# Model for the token received from the frontend
class Token(BaseModel):
    id_token: str

@auth_router.post("/auth/google")
async def google_login(token: Token):
    """
    Authenticate the user using Google OAuth 2.0 and return user info.
    """
    logging.info("Received token for authentication")
    try:
        # Verify the token with Google's API
        id_info = id_token.verify_oauth2_token(token.id_token, requests.Request(), GOOGLE_CLIENT_ID)
        logging.info(f"Token verified successfully: {id_info}")

        # Check if the token is issued by Google
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logging.error(f"Invalid token issuer: {id_info['iss']}")
            raise HTTPException(status_code=403, detail="Invalid token issuer.")

        # Extract user info from the token
        user_id = id_info['sub']
        email = id_info.get('email')
        first_name = id_info.get('given_name')
        last_name = id_info.get('family_name')

        logging.info(f"User authenticated: {email}")

        # Here, you can perform any additional logic: TODO TODO
        # - Check if the user exists in your database
        # - Register the user if they are new
        # - Create and return a JWT for your system if needed

        return {
            "user_id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }

    except ValueError as e:
        # Invalid token
        logging.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid token.")
    except Exception as e:
        # General exception
        logging.error(f"An error occurred during authentication: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
