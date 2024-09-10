from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils import config
from api.events import case_insensitive_router, startup_event
from api.routes import api_router


def init_app() -> FastAPI:
    """Initialize the FastAPI application"""

    app = FastAPI(
        title=config.API_TITLE,
        summary=config.API_SUMMARY,
        description=config.API_DESCRIPTION,
        version=config.API_VERSION,
        contact=config.API_CONTACT,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.API_ALLOWED_ORIGINS,
        allow_methods=["OPTIONS", "POST", "GET", "PUT", "PATCH", "DELETE"],
        allow_headers=["*"]
    )
    app.include_router(api_router)
    app.on_event("startup")(startup_event)
    app.middleware("http")(case_insensitive_router)

    return app


app = init_app()


def run_uvicorn():
    """Run the application with uvicorn"""

    from utils import config
    from sys import argv
    reload = "-hr" in argv or "--reload" in argv
    port = 8080 if reload else config.API_PORT

    from uvicorn import run
    run('main:app',
        reload=reload,
        workers=1,
        host=config.API_HOST,
        port=port)


if __name__ == "__main__":
    run_uvicorn()
