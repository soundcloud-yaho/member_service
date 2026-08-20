# [스키마] 요청/응답 형식 — 프론트와 합의된 필드명, 임의 변경 금지

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserSchema(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSchema


class FavoriteAddRequest(BaseModel):
    team_id: int


class FavoriteTeamIdsResponse(BaseModel):
    team_ids: list[int]


class FavoriteTeamResponse(BaseModel):
    team_id: int