from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CommentCreate(BaseModel):
    """
    댓글 작성 요청 형식
    """

    match_id: int = Field(gt=0)
    content: str = Field(min_length=1, max_length=300)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        # 댓글 앞뒤 공백 제거
        normalized = value.strip()

        # 공백만 입력한 댓글 차단
        if not normalized:
            raise ValueError("댓글 내용을 입력해주세요.")

        return normalized


class CommentUpdate(BaseModel):
    """
    댓글 수정 요청 형식
    """

    content: str = Field(min_length=1, max_length=300)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("댓글 내용을 입력해주세요.")

        return normalized


class CommentResponse(BaseModel):
    """
    댓글 응답 형식
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    user_id: int
    username: str
    content: str
    created_at: datetime
    updated_at: datetime


class CommentListResponse(BaseModel):
    """
    댓글 목록 조회 응답 형식
    """

    comments: list[CommentResponse]
    next_after_id: int | None