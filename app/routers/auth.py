# [API] 회원가입 / 로그인 / 내 정보 조회
# POST /auth/register
# POST /auth/login
# GET  /auth/me

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models.tables import User
from app.models.schemas import RegisterRequest, LoginRequest, LoginResponse, UserSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserSchema, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    회원가입
    - username 중복이면 409
    """
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    로그인
    - 아이디 없거나 비밀번호 불일치면 동일하게 401
      (계정 존재 여부가 노출되지 않도록 메시지를 통일함)
    """
    user = db.query(User).filter(User.username == payload.username).first()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    token = create_access_token(user.id, user.username)

    return LoginResponse(access_token=token, user=user)


@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    """
    내 정보 조회 (토큰 유효성 검증 겸용)
    """
    return current_user
