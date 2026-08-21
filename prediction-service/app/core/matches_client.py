from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, status

from app.core.config import MATCHES_SERVICE_URL


EDITABLE_MATCH_STATUSES = {"SCHEDULED", "TIMED"}


async def get_match(match_id: int) -> dict:
    url = f"{MATCHES_SERVICE_URL}/matches/{match_id}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="경기 조회 서비스에 연결할 수 없습니다.",
        ) from exc

    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 경기입니다.",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="경기 정보를 정상적으로 조회하지 못했습니다.",
        )

    return response.json()


def ensure_prediction_is_open(match: dict) -> None:
    match_status = str(match.get("status", "")).upper()

    if match_status not in EDITABLE_MATCH_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="예측을 등록하거나 수정할 수 없는 경기 상태입니다.",
        )

    match_date_value = match.get("match_date")

    if not match_date_value:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="경기 시작 시간 정보가 없습니다.",
        )

    try:
        match_date = datetime.fromisoformat(
            str(match_date_value).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="경기 시작 시간 형식이 올바르지 않습니다.",
        ) from exc

    if match_date.tzinfo is None:
        match_date = match_date.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) >= match_date.astimezone(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="경기가 시작되어 예측을 등록하거나 수정할 수 없습니다.",
        )