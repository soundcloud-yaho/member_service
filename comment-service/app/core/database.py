from collections.abc import AsyncGenerator
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def make_database_url() -> str:
    """
    환경변수의 DB 정보를 SQLAlchemy 비동기 연결 URL로 변환합니다.
    """

    if not settings.DB_HOST:
        raise RuntimeError(
            "DB_HOST 환경변수가 필요합니다."
        )

    if not settings.DB_USER:
        raise RuntimeError(
            "DB_USER 환경변수가 필요합니다."
        )

    if not settings.DB_PASSWORD:
        raise RuntimeError(
            "DB_PASSWORD 환경변수가 필요합니다."
        )

    user = quote_plus(settings.DB_USER)
    password = quote_plus(settings.DB_PASSWORD)

    return (
        f"postgresql+asyncpg://{user}:{password}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}"
        f"/{settings.DB_NAME}"
    )


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    make_database_url(),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=10,
    pool_timeout=5,
)


SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def create_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )


async def check_db_connection() -> bool:
    try:
        async with engine.connect() as connection:
            await connection.execute(
                text("SELECT 1")
            )

        return True

    except Exception:
        return False