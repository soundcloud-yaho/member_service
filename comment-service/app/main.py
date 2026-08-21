import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.database import check_db_connection, create_tables
from app.routers import comments


# 기본 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("comment_api_latency")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    댓글 서비스가 시작될 때 comments 테이블을 확인하고,
    테이블이 없으면 자동으로 생성합니다.
    """

    await create_tables()

    yield


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="PeakPilot Comment API",
    description="경기별 댓글 조회·작성·수정·삭제 서비스",
    version="1.0.0",
    lifespan=lifespan,
)


# Prometheus 메트릭 수집 설정
instrumentator = Instrumentator(
    should_instrument_requests_inprogress=True,
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
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


# 기존 backend와 동일한 CORS 허용 주소
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


# API 요청별 응답시간 로그
@app.middleware("http")
async def latency_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    logger.info(
        "method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    response.headers["X-Response-Time-ms"] = str(duration_ms)

    return response


# comments.py에 작성한 API 등록
app.include_router(comments.router)


@app.get("/health")
async def health_check():
    """
    기본 애플리케이션 상태 확인
    """

    return {"status": "ok"}


@app.get("/healthz")
async def healthz():
    """
    Kubernetes Liveness Probe
    """

    return {"status": "ok"}


@app.get("/readyz")
async def readyz(response: Response):
    """
    Kubernetes Readiness Probe

    DB 접속까지 성공해야 트래픽을 받을 준비가 된 것으로 처리합니다.
    """

    if await check_db_connection():
        return {"status": "ready"}

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {"status": "not_ready"}