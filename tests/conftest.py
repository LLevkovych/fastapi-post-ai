import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import User, Post, Comment
from app.auth import create_access_token, get_password_hash
import os

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """Create test database and tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    # Cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_db):
    """Create a new database session for a test."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client(db_session):
    """Create a test client with database session."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user_data = {
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "is_active": True
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_token(test_user):
    """Create access token for test user."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
async def test_post(db_session, test_user):
    """Create a test post."""
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
        "author_id": test_user.id,
        "auto_reply_enabled": True,
        "auto_reply_delay": 60
    }
    post = Post(**post_data)
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post


@pytest.fixture
async def test_comment(db_session, test_user, test_post):
    """Create a test comment."""
    comment_data = {
        "content": "This is a test comment.",
        "author_id": test_user.id,
        "post_id": test_post.id,
        "is_blocked": False,
        "is_auto_reply": False
    }
    comment = Comment(**comment_data)
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)
    return comment


@pytest.fixture
async def auth_headers(test_user_token):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {test_user_token}"} 