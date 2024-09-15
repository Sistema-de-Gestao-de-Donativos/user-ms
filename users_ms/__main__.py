import uvicorn

from .settings import Settings
from . import db


def main() -> None:
    settings = Settings()  # type: ignore
    db.init_db(settings.MONGODB_URL, settings.MONGODB_DB)
    uvicorn.run(
        app="users_ms:create_app",
        factory=True,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
        use_colors=True,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
