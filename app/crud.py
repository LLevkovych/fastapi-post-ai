from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date
from app import models, schemas
from app.auth import get_password_hash
from app.utils import logger

# User CRUD operations
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_create: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user_create.password)
    db_user = models.User(email=user_create.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info(f"Created new user: {db_user.email}")
    return db_user

async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user

# Post CRUD operations
async def create_post(db: AsyncSession, post_create: schemas.PostCreate, author_id: int) -> models.Post:
    db_post = models.Post(**post_create.dict(), author_id=author_id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    logger.info(f"Created new post: {db_post.title} by user {author_id}")
    return db_post

async def get_post_by_id(db: AsyncSession, post_id: int) -> Optional[models.Post]:
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    return result.scalars().first()

async def get_posts(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 10,
    author_id: Optional[int] = None
) -> List[models.Post]:
    query = select(models.Post)
    if author_id:
        query = query.where(models.Post.author_id == author_id)
    query = query.offset(skip).limit(limit).order_by(desc(models.Post.created_at))
    result = await db.execute(query)
    return result.scalars().all()

async def update_post(db: AsyncSession, post_id: int, post_update: schemas.PostUpdate, user_id: int) -> Optional[models.Post]:
    post = await get_post_by_id(db, post_id)
    if not post or post.author_id != user_id:
        return None
    
    update_data = post_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    await db.commit()
    await db.refresh(post)
    return post

async def delete_post(db: AsyncSession, post_id: int, user_id: int) -> bool:
    post = await get_post_by_id(db, post_id)
    if not post or post.author_id != user_id:
        return False
    
    await db.delete(post)
    await db.commit()
    logger.info(f"Deleted post {post_id} by user {user_id}")
    return True

# Comment CRUD operations
async def create_comment(db: AsyncSession, comment_create: schemas.CommentCreate, author_id: int, post_id: int) -> models.Comment:
    db_comment = models.Comment(**comment_create.dict(), author_id=author_id, post_id=post_id)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    logger.info(f"Created new comment by user {author_id} on post {post_id}")
    return db_comment

async def get_comment_by_id(db: AsyncSession, comment_id: int) -> Optional[models.Comment]:
    result = await db.execute(select(models.Comment).where(models.Comment.id == comment_id))
    return result.scalars().first()

async def get_comments_by_post(
    db: AsyncSession, 
    post_id: int, 
    skip: int = 0, 
    limit: int = 50,
    include_blocked: bool = False
) -> List[models.Comment]:
    query = select(models.Comment).where(models.Comment.post_id == post_id)
    if not include_blocked:
        query = query.where(models.Comment.is_blocked == False)
    query = query.offset(skip).limit(limit).order_by(desc(models.Comment.created_at))
    result = await db.execute(query)
    return result.scalars().all()

async def update_comment(db: AsyncSession, comment_id: int, comment_update: schemas.CommentUpdate, user_id: int) -> Optional[models.Comment]:
    comment = await get_comment_by_id(db, comment_id)
    if not comment or comment.author_id != user_id:
        return None
    
    update_data = comment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    
    await db.commit()
    await db.refresh(comment)
    return comment

async def delete_comment(db: AsyncSession, comment_id: int, user_id: int) -> bool:
    comment = await get_comment_by_id(db, comment_id)
    if not comment or comment.author_id != user_id:
        return False
    
    await db.delete(comment)
    await db.commit()
    logger.info(f"Deleted comment {comment_id} by user {user_id}")
    return True

async def block_comment(db: AsyncSession, comment_id: int) -> Optional[models.Comment]:
    comment = await get_comment_by_id(db, comment_id)
    if not comment:
        return None
    
    comment.is_blocked = True
    await db.commit()
    await db.refresh(comment)
    logger.warning(f"Blocked comment {comment_id}")
    return comment

# Analytics operations
async def get_comments_daily_breakdown(
    db: AsyncSession, 
    date_from: date, 
    date_to: date
) -> List[dict]:
    """Отримання аналітики коментарів по днях"""
    query = select(
        func.date(models.Comment.created_at).label('date'),
        func.count(models.Comment.id).label('total_comments'),
        func.sum(func.case((models.Comment.is_blocked == True, 1), else_=0)).label('blocked_comments')
    ).where(
        and_(
            func.date(models.Comment.created_at) >= date_from,
            func.date(models.Comment.created_at) <= date_to
        )
    ).group_by(
        func.date(models.Comment.created_at)
    ).order_by(
        func.date(models.Comment.created_at)
    )
    
    result = await db.execute(query)
    return [
        {
            "date": row.date,
            "total_comments": row.total_comments,
            "blocked_comments": row.blocked_comments,
            "active_comments": row.total_comments - row.blocked_comments
        }
        for row in result.all()
    ]
