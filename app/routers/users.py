from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserRead, UserUpdate
from app.database import get_db
from app import crud, auth
from app.utils import logger

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user = Depends(auth.get_current_active_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserRead)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    # Check if email is not taken by another user
    if user_update.email and user_update.email != current_user.email:
        existing_user = await crud.get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user
    updated_user = await crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"User {current_user.id} updated profile")
    return updated_user 