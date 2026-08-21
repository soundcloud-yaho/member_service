from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    # match_id별 댓글을 id 순서로 빠르게 조회하기 위한 인덱스
    __table_args__ = (
        Index("ix_comments_match_id_id", "match_id", "id"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # matches 서비스의 경기 ID
    # 서비스 DB가 분리되어 있으므로 FK는 설정하지 않습니다.
    match_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # member 서비스의 사용자 ID
    # member DB와 FK로 연결하지 않고 값만 저장합니다.
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )