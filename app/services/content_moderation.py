import os
from app.config import settings
from typing import Dict, Any
import httpx

# Google AI API endpoint (example, adjust as needed)
GOOGLE_AI_API_URL = "https://generativelanguage.googleapis.com/v1beta3/models/moderation:predict"

class ModerationResult:
    def __init__(self, is_appropriate: bool, confidence: float, issues: list, severity: str):
        self.is_appropriate = is_appropriate
        self.confidence = confidence
        self.issues = issues
        self.severity = severity

    def to_dict(self):
        return {
            "is_appropriate": self.is_appropriate,
            "confidence": self.confidence,
            "issues": self.issues,
            "severity": self.severity
        }

async def moderate_content(text: str) -> ModerationResult:
    """
    Use Google AI API to moderate content.
    Returns ModerationResult.
    """
    if not settings.GOOGLE_AI_API_KEY:
        # If no key, allow all content (for dev)
        return ModerationResult(True, 1.0, [], "none")

    headers = {"Content-Type": "application/json"}
    params = {"key": settings.GOOGLE_AI_API_KEY}
    payload = {
        "prompt": {"text": text},
        # Add more fields if required by Google API
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(GOOGLE_AI_API_URL, headers=headers, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            # Example parsing, adjust to real API response
            flagged = data.get("flagged", False)
            confidence = data.get("confidence", 1.0)
            issues = data.get("issues", [])
            severity = data.get("severity", "none")
            return ModerationResult(not flagged, confidence, issues, severity)
    except Exception as e:
        # On error, allow content but log issue
        from app.utils import logger
        logger.warning(f"AI moderation failed: {e}")
        return ModerationResult(True, 0.5, ["moderation_error"], "unknown") 