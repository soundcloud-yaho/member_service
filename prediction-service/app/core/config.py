import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    APP_NAME: str = os.getenv(
        "APP_NAME",
        "Prediction Service",
    )

    APP_PORT: int = int(
        os.getenv("APP_PORT", "8080")
    )

    DB_HOST: str = os.getenv(
        "DB_HOST",
        "localhost",
    )

    DB_PORT: str = os.getenv(
        "DB_PORT",
        "5432",
    )

    DB_NAME: str = os.getenv(
        "DB_NAME",
        "prediction",
    )

    DB_USER: str = os.getenv(
        "DB_USER",
        "postgres",
    )

    DB_PASSWORD: str = os.getenv(
        "DB_PASSWORD",
        "",
    )

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "",
    )

    JWT_ALGORITHM: str = os.getenv(
        "JWT_ALGORITHM",
        "HS256",
    )

    MATCHES_SERVICE_URL: str = os.getenv(
        "MATCHES_SERVICE_URL",
        "http://backend:8080",
    ).rstrip("/")


settings = Settings()


def make_database_url() -> str:
    return (
        f"postgresql+asyncpg://"
        f"{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}"
        f"/{settings.DB_NAME}"
    )