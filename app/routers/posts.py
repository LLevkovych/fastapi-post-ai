from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.schemas import PostCreate, PostRead, PostUpdate, PostList, PaginationParams
from app.database import get_db
from app import crud, auth
from app.utils import logger, paginate_results
from app.services import content_moderation

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=PostList)
async def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of posts with pagination"""
    skip = (page - 1) * page_size
    
    # Get posts
    posts = await crud.get_posts(db, skip=skip, limit=page_size, author_id=author_id)
    
    # Get total count for pagination
    total_posts = await crud.get_posts(db, skip=0, limit=1000, author_id=author_id)
    total = len(total_posts)
    
    # Format response with pagination
    paginated_result = paginate_results(posts, page, page_size)
    paginated_result["total"] = total
    
    return PostList(
        posts=posts,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_create: PostCreate,
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new post with AI moderation"""
    # Moderate post content using AI
    moderation_result = await content_moderation.moderate_content(
        f"{post_create.title} {post_create.content}", "post"
    )
    
    # Check if content is appropriate
    if not moderation_result["is_appropriate"]:
        logger.warning(f"Post blocked due to inappropriate content: {moderation_result}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Post contains inappropriate content",
                "issues": moderation_result.get("issues", []),
                "severity": moderation_result.get("severity", "medium")
            }
        )
    
    # Create post
    post = await crud.create_post(db, post_create, current_user.id)
    logger.info(f"User {current_user.id} created post: {post.title} (moderated)")
    return post


@router.get("/{post_id}", response_model=PostRead)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get post by ID"""
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post


@router.put("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update post"""
    post = await crud.update_post(db, post_id, post_update, current_user.id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to edit it"
        )
    
    logger.info(f"User {current_user.id} updated post: {post.title}")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete post"""
    success = await crud.delete_post(db, post_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )
    
    logger.info(f"User {current_user.id} deleted post: {post_id}")
    return None 