# 1단계: Python 라이브러리 설치
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


# 2단계: 실제 댓글 서비스 실행 이미지
FROM python:3.11-slim

WORKDIR /app

# root가 아닌 일반 사용자 생성
RUN adduser \
    --disabled-password \
    --gecos "" \
    appuser

# 1단계에서 설치한 Python 라이브러리 복사
COPY --from=builder /install /usr/local

# comment-service 코드 복사
COPY . .

# 파일 소유권 변경
RUN chown -R appuser:appuser /app

# 일반 사용자로 실행
USER appuser

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8080}"]