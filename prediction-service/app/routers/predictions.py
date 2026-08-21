from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.matches_client import ensure_prediction_is_open, get_match
from app.core.security import CurrentUser, get_current_user
from app.models.schemas import (
    MatchPredictionSummary,
    PredictionCount,
    PredictionCreate,
    PredictionResponse,
    PredictionUpdate,
)
from app.models.tables import Prediction


router = APIRouter(
    prefix="/predictions",
    tags=["predictions"],
)


@router.post(
    "",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_prediction(
    request: PredictionCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    match = await get_match(request.match_id)
    ensure_prediction_is_open(match)

    user_id = current_user.id

    existing_query = select(Prediction).where(
        Prediction.user_id == user_id,
        Prediction.match_id == request.match_id,
    )
    existing = await db.scalar(existing_query)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 해당 경기에 예측을 등록했습니다.",
        )

    prediction = Prediction(
        user_id=user_id,
        match_id=request.match_id,
        predicted_result=request.predicted_result.value,
    )

    db.add(prediction)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 해당 경기에 예측을 등록했습니다.",
        ) from exc

    await db.refresh(prediction)

    return prediction


@router.put(
    "/{prediction_id}",
    response_model=PredictionResponse,
)
async def update_prediction(
    prediction_id: int,
    request: PredictionUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id

    query = select(Prediction).where(
        Prediction.id == prediction_id,
    )
    prediction = await db.scalar(query)

    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="예측 정보를 찾을 수 없습니다.",
        )

    if prediction.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 예측만 수정할 수 있습니다.",
        )

    match = await get_match(prediction.match_id)
    ensure_prediction_is_open(match)

    prediction.predicted_result = request.predicted_result.value

    await db.commit()
    await db.refresh(prediction)

    return prediction


@router.get(
    "/me",
    response_model=list[PredictionResponse],
)
async def list_my_predictions(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id

    query = (
        select(Prediction)
        .where(Prediction.user_id == user_id)
        .order_by(Prediction.created_at.desc())
    )

    result = await db.scalars(query)

    return list(result.all())


@router.get(
    "/matches/{match_id}",
    response_model=MatchPredictionSummary,
)
async def get_match_prediction_summary(
    match_id: int,
    db: AsyncSession = Depends(get_db),
):
    query = select(
        func.count(Prediction.id).label("total"),
        func.sum(
            case(
                (Prediction.predicted_result == "HOME", 1),
                else_=0,
            )
        ).label("home"),
        func.sum(
            case(
                (Prediction.predicted_result == "DRAW", 1),
                else_=0,
            )
        ).label("draw"),
        func.sum(
            case(
                (Prediction.predicted_result == "AWAY", 1),
                else_=0,
            )
        ).label("away"),
    ).where(
        Prediction.match_id == match_id,
    )

    result = (await db.execute(query)).one()

    return MatchPredictionSummary(
        match_id=match_id,
        total=result.total or 0,
        counts=PredictionCount(
            home=result.home or 0,
            draw=result.draw or 0,
            away=result.away or 0,
        ),
    )