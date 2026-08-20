# [DB] 커넥션 — 이 서비스는 트래픽이 크지 않다고 가정하고
# matches 서비스처럼 Writer/Reader를 나누지 않고 단일 커넥션으로 단순화함

from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


def make_database_url() -> str:
    user = quote_plus(settings.DB_USER)
    password = quote_plus(settings.DB_PASSWORD)
    return (
        f"postgresql://{user}:{password}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


engine = create_engine(
    make_database_url(),
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=3,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
