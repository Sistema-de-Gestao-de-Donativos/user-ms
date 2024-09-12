from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from ..settings import Settings

api_key_header_object = APIKeyHeader(name="x-access-token", scheme_name="API Key")
sets = Settings()  # type: ignore


def validate_api_key(x_token: str = Security(api_key_header_object)) -> None:
    if x_token != sets.API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid token provided.")
