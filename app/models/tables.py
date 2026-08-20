# [DB 모델] users, favorites 테이블

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Favorite(Base):
    __tablename__ = "favorites"
    # team_id는 matches 서비스(다른 DB)의 Team.id 값.
    # 서비스가 분리되어 있어 FK로 묶을 수 없음 — 값 기준으로만 정합성을 맞춤.

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    team_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uq_user_team_favorite"),
    )