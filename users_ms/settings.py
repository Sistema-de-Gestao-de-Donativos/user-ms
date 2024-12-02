from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Uvicorn config
    HOST: str = "0.0.0.0"
    RELOAD: bool = False
    WORKERS: int = 2
    MONGO_DB_URL: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "users-ms"
    PORT: int = 8000
    API_SECRET: str = "super-secret"
    JWT_PUBLIC_KEY: str = "jwt-public"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file="environments/.env",
    )
