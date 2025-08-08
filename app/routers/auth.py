from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, UserRead, UserLogin, Token, TokenRefresh
from app.database import get_db
from app import crud, auth
from app.utils import logger

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register new user"""
    # Check if user already exists
    existing_user = await crud.get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await crud.create_user(db, user_create)
    logger.info(f"New user registered: {user.email}")
    
    return user


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user and return access tokens"""
    # Authenticate user
    login_result = await auth.login_user(db, user_login.email, user_login.password)
    
    if not login_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    logger.info(f"User logged in: {user_login.email}")
    return login_result


@router.post("/refresh", response_model=Token)
async def refresh_token(token_refresh: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""
    # Verify refresh token
    payload = auth.verify_refresh_token(token_refresh.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Refresh access token
    refresh_result = await auth.refresh_access_token(token_refresh.refresh_token, db)
    if not refresh_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    logger.info(f"Token refreshed for user: {payload.get('sub')}")
    return refresh_result 