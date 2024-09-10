from fastapi import APIRouter

from api.endpoints import access, auth
from utils.api import ApiResponse


api_router = APIRouter()
api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(access.router, prefix="/access", tags=["Access"])

@api_router.get("/")
def main():
    return ApiResponse(
        message="Bem vindo a API de acesso",
        data={
            "swagger (documentation)": "/docs",
            "authors": "Ramiro Barros, Vinicius Turani"
        }
    )
