from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.models.schemas import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from app.models.tables import Comment


router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)


@router.get(
    "",
    response_model=CommentListResponse,
)
async def list_comments(
    match_id: int = Query(gt=0),
    after_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CommentListResponse:
    """
    특정 경기의 댓글을 조회합니다.

    after_id가 전달되면 해당 ID 이후의 댓글만 반환합니다.
    """

    query = select(Comment).where(
        Comment.match_id == match_id
    )

    if after_id is not None:
        query = query.where(
            Comment.id > after_id
        )

    query = query.order_by(
        Comment.id.asc()
    ).limit(limit)

    result = await db.scalars(query)
    comments = list(result.all())

    return CommentListResponse(
        comments=[
            CommentResponse.model_validate(comment)
            for comment in comments
        ],
        next_after_id=comments[-1].id if comments else after_id,
    )


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    request: CommentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Comment:
    """
    로그인한 사용자가 댓글을 작성합니다.
    """

    comment = Comment(
        match_id=request.match_id,
        user_id=current_user.id,
        username=current_user.username,
        content=request.content,
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return comment


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    comment_id: int,
    request: CommentUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Comment:
    """
    작성자 본인의 댓글을 수정합니다.
    """

    comment = await db.get(Comment, comment_id)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다.",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 댓글만 수정할 수 있습니다.",
        )

    comment.content = request.content

    await db.commit()
    await db.refresh(comment)

    return comment


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    작성자 본인의 댓글을 삭제합니다.
    """

    comment = await db.get(Comment, comment_id)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다.",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 댓글만 삭제할 수 있습니다.",
        )

    await db.delete(comment)
    await db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )