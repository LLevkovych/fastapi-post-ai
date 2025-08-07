import asyncio
from app.config import settings
from app.models import Post, Comment, User
from app.database import SessionLocal
from app.services.content_moderation import moderate_content
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.utils import logger

# Для генерації відповіді можна використати Google AI або OpenAI
GOOGLE_AI_API_URL = "https://generativelanguage.googleapis.com/v1beta3/models/gemini-pro:generateContent"

async def generate_auto_reply(post: Post, comment: Comment) -> str:
    """
    Generate a relevant auto-reply using Google AI API.
    """
    if not settings.GOOGLE_AI_API_KEY:
        return "Thank you for your comment!"
    prompt = f"Post: {post.title}\n{post.content}\nComment: {comment.content}\nReply as the author:"
    headers = {"Content-Type": "application/json"}
    params = {"key": settings.GOOGLE_AI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(GOOGLE_AI_API_URL, headers=headers, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            # Витягуємо відповідь з AI (приклад, залежить від API)
            reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Thank you!")
            return reply.strip()
    except Exception as e:
        logger.warning(f"AI auto-reply failed: {e}")
        return "Thank you for your comment!"

async def schedule_auto_reply(post_id: int, comment_id: int, delay: int = 60):
    """
    Schedule an auto-reply after a delay (in seconds).
    """
    await asyncio.sleep(delay)
    async with SessionLocal() as db:
        post = await db.get(Post, post_id)
        comment = await db.get(Comment, comment_id)
        if not post or not comment:
            return
        # Перевіряємо чи ще не було відповіді
        existing = await db.execute(select(Comment).where(
            Comment.post_id == post_id,
            Comment.author_id == post.author_id,
            Comment.content.like("[Auto-reply]%"),
            Comment.created_at > comment.created_at
        ))
        if existing.scalars().first():
            return
        reply_text = await generate_auto_reply(post, comment)
        auto_reply = Comment(
            content=f"[Auto-reply] {reply_text}",
            author_id=post.author_id,
            post_id=post_id,
            is_blocked=False
        )
        db.add(auto_reply)
        await db.commit()
        await db.refresh(auto_reply)
        logger.info(f"Auto-reply added to post {post_id} for comment {comment_id}")
