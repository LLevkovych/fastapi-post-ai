from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta
from typing import List
from app.schemas import CommentsDailyBreakdown, AnalyticsResponse
from app.database import get_db
from app import crud, auth
from app.utils import logger

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/comments-daily-breakdown", response_model=AnalyticsResponse)
async def get_comments_daily_breakdown(
    date_from: date = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to: date = Query(..., description="End date (YYYY-MM-DD)"),
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get daily breakdown of comments for analytics"""
    # Validate dates
    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from cannot be later than date_to"
        )
    
    # Check if period is not too large
    days_diff = (date_to - date_from).days
    if days_diff > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 365 days"
        )
    
    # Get analytics data
    breakdown_data = await crud.get_comments_daily_breakdown(db, date_from, date_to)
    
    # Calculate summary statistics
    total_comments = sum(item["total_comments"] for item in breakdown_data)
    total_blocked = sum(item["blocked_comments"] for item in breakdown_data)
    total_active = sum(item["active_comments"] for item in breakdown_data)
    
    summary = {
        "total_comments": total_comments,
        "total_blocked": total_blocked,
        "total_active": total_active,
        "blocked_percentage": round((total_blocked / total_comments * 100) if total_comments > 0 else 0, 2),
        "period_days": days_diff + 1,
        "average_comments_per_day": round(total_comments / (days_diff + 1), 2) if days_diff > 0 else total_comments
    }
    
    # Convert to schemas
    comments_breakdown = [
        CommentsDailyBreakdown(
            date=item["date"],
            total_comments=item["total_comments"],
            blocked_comments=item["blocked_comments"],
            active_comments=item["active_comments"]
        )
        for item in breakdown_data
    ]
    
    period = f"{date_from} to {date_to}"
    
    logger.info(f"User {current_user.id} requested analytics for period: {period}")
    
    return AnalyticsResponse(
        period=period,
        data=comments_breakdown,
        summary=summary
    )


@router.get("/comments-daily-breakdown/last-30-days", response_model=AnalyticsResponse)
async def get_comments_last_30_days(
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comments analytics for last 30 days"""
    date_to = date.today()
    date_from = date_to - timedelta(days=29)
    
    return await get_comments_daily_breakdown(date_from, date_to, current_user, db)


@router.get("/comments-daily-breakdown/last-7-days", response_model=AnalyticsResponse)
async def get_comments_last_7_days(
    current_user = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comments analytics for last 7 days"""
    date_to = date.today()
    date_from = date_to - timedelta(days=6)
    
    return await get_comments_daily_breakdown(date_from, date_to, current_user, db) 