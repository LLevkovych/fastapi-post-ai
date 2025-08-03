import logging
from datetime import datetime, timezone
from typing import Optional
from loguru import logger
from app.config import settings

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL,
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)
logger.add(
    lambda msg: print(msg, end=""),  # Console output
    level=settings.LOG_LEVEL,
    format="{time:HH:mm:ss} | {level} | {message}"
)


def get_current_time() -> datetime:
    """Get current time in UTC"""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def validate_email(email: str) -> bool:
    """Validate email address format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_text(text: str) -> str:
    """Sanitize text by escaping HTML characters"""
    import html
    return html.escape(text.strip())


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    import re
    import unicodedata
    
    # Normalize Unicode characters
    title = unicodedata.normalize('NFKD', title)
    
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    
    return slug.strip('-')


def paginate_results(items: list, page: int = 1, page_size: int = 10) -> dict:
    """Paginate results with metadata"""
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


def log_user_action(user_id: int, action: str, details: Optional[dict] = None):
    """Log user actions for audit trail"""
    logger.info(f"User {user_id} performed action: {action}", extra={
        "user_id": user_id,
        "action": action,
        "details": details or {}
    })


def log_moderation_action(content_type: str, content_id: int, action: str, reason: Optional[str] = None):
    """Log moderation actions for audit trail"""
    logger.warning(f"Moderation: {action} on {content_type} {content_id}", extra={
        "content_type": content_type,
        "content_id": content_id,
        "action": action,
        "reason": reason
    })
