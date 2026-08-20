# [엔트리] FastAPI 앱 생성, 라우터 등록, 헬스체크

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth, favorites

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("member_service")

app = FastAPI(
    title="Member Service API",
    description="회원가입/로그인/인증을 담당하는 서비스",
    version="1.0.0",
)

# 프론트엔드 주소 — matches 서비스의 origins 목록과 동일하게 맞춰둠
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    # 나중에 프론트 배포 주소 추가
    # "https://프론트도메인",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 개발 초기: 테이블 없으면 자동 생성 (운영 전환 시 알렘빅 등 마이그레이션 도구로 교체 권장)
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(favorites.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}