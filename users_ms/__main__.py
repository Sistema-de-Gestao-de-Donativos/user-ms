import uvicorn

from .settings import Settings


def main() -> None:
    settings = Settings()  # type: ignore
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
