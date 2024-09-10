from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Uvicorn config
    WORKERS: int = 1
    HOST: str = "0.0.0.0"
    ORIGINS: list[str] = ["*"]
    PORT: int = 5000
    RELOAD: bool = False
