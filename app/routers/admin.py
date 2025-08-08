from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CommentRead
from app.database import get_db
from app import crud, auth
from app.utils import logger

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/comments/{comment_id}/block", response_model=CommentRead)
async def block_comment(
    comment_id: int,
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Block comment (administrative function)"""
    comment = await crud.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if comment.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment is already blocked"
        )
    
    blocked_comment = await crud.block_comment(db, comment_id)
    if not blocked_comment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to block comment"
        )
    
    author = await crud.get_user_by_id(db, blocked_comment.author_id)
    blocked_comment.author_email = author.email if author else None
    
    logger.warning(f"Admin user {current_user.id} blocked comment {comment_id}")
    return blocked_comment


@router.post("/comments/{comment_id}/unblock", response_model=CommentRead)
async def unblock_comment(
    comment_id: int,
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Unblock comment (administrative function)"""
    comment = await crud.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if not comment.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment is not blocked"
        )
    
    comment.is_blocked = False
    await db.commit()
    await db.refresh(comment)
    
    author = await crud.get_user_by_id(db, comment.author_id)
    comment.author_email = author.email if author else None
    
    logger.info(f"Admin user {current_user.id} unblocked comment {comment_id}")
    return comment 