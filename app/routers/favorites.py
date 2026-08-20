# [API] 팀 즐겨찾기 — 전부 로그인 필요 (get_current_user 재사용)
# GET    /favorites
# POST   /favorites
# DELETE /favorites/{team_id}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.tables import User, Favorite
from app.models.schemas import (
    FavoriteAddRequest,
    FavoriteTeamIdsResponse,
    FavoriteTeamResponse,
)

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=FavoriteTeamIdsResponse)
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    내 즐겨찾기 팀 id 목록 조회
    """
    rows = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return FavoriteTeamIdsResponse(team_ids=[r.team_id for r in rows])


@router.post("", response_model=FavoriteTeamResponse, status_code=201)
def add_favorite(
    payload: FavoriteAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    팀 즐겨찾기 추가
    - 이미 즐겨찾기한 팀이면 409
    """
    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.team_id == payload.team_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="이미 즐겨찾기한 팀입니다.")

    favorite = Favorite(user_id=current_user.id, team_id=payload.team_id)
    db.add(favorite)
    db.commit()

    return FavoriteTeamResponse(team_id=payload.team_id)


@router.delete("/{team_id}", status_code=204)
def remove_favorite(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    팀 즐겨찾기 삭제
    - 즐겨찾기하지 않은 팀이면 404
    """
    favorite = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.team_id == team_id)
        .first()
    )
    if favorite is None:
        raise HTTPException(status_code=404, detail="즐겨찾기하지 않은 팀입니다.")

    db.delete(favorite)
    db.commit()
