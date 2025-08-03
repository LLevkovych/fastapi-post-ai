from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.schemas import CommentCreate, CommentRead, CommentUpdate, CommentList
from app.database import get_db
from app import crud, auth
from app.utils import logger, paginate_results

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.get("/", response_model=CommentList)
async def get_comments(
    post_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    include_blocked: bool = Query(False, description="Include blocked comments"),
    db: AsyncSession = Depends(get_db)
):
    """Get comments for a post"""
    # Check if post exists
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    skip = (page - 1) * page_size
    
    # Get comments
    comments = await crud.get_comments_by_post(
        db, post_id, skip=skip, limit=page_size, include_blocked=include_blocked
    )
    
    # Get total count
    all_comments = await crud.get_comments_by_post(
        db, post_id, skip=0, limit=1000, include_blocked=include_blocked
    )
    total = len(all_comments)
    
    # Add author email to each comment
    for comment in comments:
        author = await crud.get_user_by_id(db, comment.author_id)
        comment.author_email = author.email if author else None
    
    return CommentList(
        comments=comments,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.post("/", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment_create: CommentCreate,
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new comment"""
    # Check if post exists
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Create comment
    comment = await crud.create_comment(db, comment_create, current_user.id, post_id)
    
    # Add author email
    comment.author_email = current_user.email
    
    logger.info(f"User {current_user.id} created comment on post {post_id}")
    return comment


@router.put("/comments/{comment_id}", response_model=CommentRead)
async def update_comment(
    post_id: int,
    comment_id: int,
    comment_update: CommentUpdate,
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update comment"""
    # Check if comment exists and belongs to the post
    comment = await crud.get_comment_by_id(db, comment_id)
    if not comment or comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Update comment
    updated_comment = await crud.update_comment(db, comment_id, comment_update, current_user.id)
    if not updated_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to edit it"
        )
    
    # Add author email
    updated_comment.author_email = current_user.email
    
    logger.info(f"User {current_user.id} updated comment {comment_id}")
    return updated_comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_id: int,
    comment_id: int,
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete comment"""
    # Check if comment exists and belongs to the post
    comment = await crud.get_comment_by_id(db, comment_id)
    if not comment or comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Delete comment
    success = await crud.delete_comment(db, comment_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )
    
    logger.info(f"User {current_user.id} deleted comment {comment_id}")
    return None 