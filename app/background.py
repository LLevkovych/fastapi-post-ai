from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.services import auto_reply
from app import crud
from app.utils import logger
import asyncio
from datetime import datetime
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "fastpostai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.background"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)


@celery_app.task(bind=True)
def generate_auto_reply(self, comment_id: int, post_id: int, delay_seconds: int = 60):
    """
    Generate and post automatic reply to a comment
    
    Args:
        comment_id: ID of the comment to reply to
        post_id: ID of the post
        delay_seconds: Delay before posting reply (default 60 seconds)
    """
    try:
        logger.info(f"Starting auto-reply task for comment {comment_id}")
        
        # Create async session
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _generate_auto_reply_async(comment_id, post_id, delay_seconds, async_session)
            )
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in auto-reply task: {e}")
        # Retry task with exponential backoff
        raise self.retry(countdown=60, max_retries=3)


async def _generate_auto_reply_async(
    comment_id: int, 
    post_id: int, 
    delay_seconds: int,
    async_session: sessionmaker
):
    """Async function to generate and post auto-reply"""
    
    async with async_session() as db:
        try:
            # Get comment and post data
            comment = await crud.get_comment(db, comment_id)
            if not comment:
                logger.error(f"Comment {comment_id} not found")
                return {"success": False, "error": "Comment not found"}
            
            post = await crud.get_post(db, post_id)
            if not post:
                logger.error(f"Post {post_id} not found")
                return {"success": False, "error": "Post not found"}
            
            # Check if auto-reply is still enabled for this post
            if not post.auto_reply_enabled:
                logger.info(f"Auto-reply disabled for post {post_id}")
                return {"success": False, "error": "Auto-reply disabled"}
            
            # Check if comment is still active (not blocked)
            if comment.is_blocked:
                logger.info(f"Comment {comment_id} is blocked, skipping auto-reply")
                return {"success": False, "error": "Comment blocked"}
            
            # Generate reply using AI
            reply_content = await auto_reply.generate_reply(
                post_content=post.content,
                comment_content=comment.content,
                post_title=post.title
            )
            
            if not reply_content:
                logger.warning(f"Failed to generate auto-reply for comment {comment_id}")
                return {"success": False, "error": "Failed to generate reply"}
            
            # Create auto-reply comment
            auto_reply_data = {
                "content": reply_content,
                "author_id": post.author_id,  # Reply as post author
                "post_id": post_id,
                "is_auto_reply": True  # Mark as auto-reply
            }
            
            # Add auto-reply comment to database
            new_reply = await crud.create_comment(db, auto_reply_data)
            
            logger.info(f"Auto-reply posted successfully: {new_reply.id}")
            
            return {
                "success": True,
                "reply_id": new_reply.id,
                "comment_id": comment_id,
                "post_id": post_id
            }
            
        except Exception as e:
            logger.error(f"Error in auto-reply async function: {e}")
            return {"success": False, "error": str(e)}


@celery_app.task
def cleanup_old_tasks():
    """Clean up old completed tasks from Redis"""
    try:
        # This is handled automatically by Celery
        logger.info("Task cleanup completed")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error in task cleanup: {e}")
        return {"success": False, "error": str(e)}


# Schedule periodic tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks"""
    # Clean up old tasks every hour
    sender.add_periodic_task(
        3600.0,  # 1 hour
        cleanup_old_tasks.s(),
        name="cleanup-old-tasks"
    )


def schedule_auto_reply(comment_id: int, post_id: int, delay_seconds: int = 60):
    """
    Schedule an auto-reply task
    
    Args:
        comment_id: ID of the comment to reply to
        post_id: ID of the post
        delay_seconds: Delay before posting reply
    """
    try:
        # Schedule task with delay
        task = generate_auto_reply.apply_async(
            args=[comment_id, post_id, delay_seconds],
            countdown=delay_seconds
        )
        
        logger.info(f"Auto-reply scheduled for comment {comment_id}, task ID: {task.id}")
        return task.id
        
    except Exception as e:
        logger.error(f"Error scheduling auto-reply: {e}")
        return None


def cancel_auto_reply(task_id: str):
    """
    Cancel a scheduled auto-reply task
    
    Args:
        task_id: ID of the task to cancel
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        logger.info(f"Auto-reply task {task_id} cancelled")
        return True
    except Exception as e:
        logger.error(f"Error cancelling auto-reply task: {e}")
        return False 