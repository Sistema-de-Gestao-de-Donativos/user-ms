from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Uvicorn config
    HOST: str = "0.0.0.0"
    RELOAD: bool = False
    WORKERS: int = 2
    MONGO_DB_URL: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "users-ms"
    PORT: int = 8000
    API_SECRET: str = "super-secret"

    class Config:
        env_file = ".env"
