from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_create):
    hashed_password = pwd_context.hash(user_create.password)
    db_user = models.User(email=user_create.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
