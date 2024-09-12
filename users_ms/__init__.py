from fastapi import FastAPI
from .api.users.routes import router as users_router
from .api.users.auth.auth import router as auth_router
from .dependencies import lifespan

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    # Include the user and auth routers
    app.include_router(users_router)
    app.include_router(auth_router, prefix="/auth", tags=["auth"])

    return app
