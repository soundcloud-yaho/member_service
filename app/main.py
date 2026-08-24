# [엔트리] FastAPI 앱 생성, 라우터 등록, 헬스체크 및 Prometheus 메트릭

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from app.core.database import Base, engine
from app.routers import auth, favorites


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("member_service")


app = FastAPI(
    title="Member Service API",
    description="회원가입/로그인/인증을 담당하는 서비스",
    version="1.0.0",
)


# 로컬 개발 및 운영 프론트엔드 주소
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://rubao.store",
    "https://www.rubao.store",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prometheus 메트릭 수집
instrumentator = Instrumentator(
    excluded_handlers=[
        "/health",
        "/healthz",
        "/readyz",
        "/metrics",
        "/docs",
        "/openapi.json",
    ],
)

instrumentator.instrument(app).expose(app)


# 개발 초기: 테이블 없으면 자동 생성
# 운영 전환 시 Alembic 등의 마이그레이션 도구로 교체 권장
Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(favorites.router)


@app.get("/health")
def health_check():
    """
    기본 애플리케이션 상태 확인
    """

    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    """
    Kubernetes Liveness Probe
    애플리케이션 프로세스의 실행 상태를 확인합니다.
    """

    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    """
    Kubernetes Readiness Probe
    DB 연결까지 성공해야 트래픽을 받을 준비가 된 것으로 처리합니다.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"status": "ready"}

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="데이터베이스 연결에 실패했습니다.",
        ) from error