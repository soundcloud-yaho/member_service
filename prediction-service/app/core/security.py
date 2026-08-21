from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings


# Authorization: Bearer <token> 형식의 토큰을 가져옵니다.
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: int
    username: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    # 토큰이 없거나 Bearer 방식이 아닌 경우
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 서버에 JWT Secret이 설정되지 않은 경우
    if not settings.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY 환경변수가 필요합니다.")

    try:
        # 지우님 회원 서비스와 동일한 Secret 및 알고리즘으로 검증
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        user_id = payload.get("sub")
        username = payload.get("username")

        # 필요한 사용자 정보가 없는 토큰 차단
        if user_id is None or not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에 사용자 정보가 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return CurrentUser(
            id=int(user_id),
            username=str(username),
        )

    except HTTPException:
        # 위에서 직접 발생시킨 HTTPException은 그대로 전달
        raise

    except (JWTError, TypeError, ValueError) as error:
        # 서명이 다르거나, 만료됐거나, sub를 숫자로 변환할 수 없는 경우
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error