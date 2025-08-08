import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
from app.config import settings
from app.utils import logger
import asyncio
from datetime import datetime

# Configure Google AI
if settings.GOOGLE_AI_API_KEY:
    genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None
    logger.warning("Google AI API key not configured. Content moderation will be disabled.")


class ContentModerationService:
    """Service for AI-powered content moderation"""
    
    def __init__(self):
        self.model = model
        self.moderation_enabled = settings.MODERATION_ENABLED and self.model is not None
    
    async def moderate_content(self, content: str, content_type: str = "comment") -> Dict:
        """
        Moderate content using Google AI
        
        Args:
            content: Text content to moderate
            content_type: Type of content ('post' or 'comment')
            
        Returns:
            Dict with moderation results
        """
        if not self.moderation_enabled:
            return {
                "is_appropriate": True,
                "confidence": 1.0,
                "issues": [],
                "moderated": False
            }
        
        try:
            # Create moderation prompt
            prompt = self._create_moderation_prompt(content, content_type)
            
            # Get AI response
            response = await self._get_ai_response(prompt)
            
            # Parse response
            result = self._parse_moderation_response(response)
            
            logger.info(f"Content moderation completed for {content_type}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in content moderation: {e}")
            # Fallback: allow content if moderation fails
            return {
                "is_appropriate": True,
                "confidence": 0.5,
                "issues": ["Moderation service unavailable"],
                "moderated": False
            }
    
    def _create_moderation_prompt(self, content: str, content_type: str) -> str:
        """Create prompt for content moderation"""
        return f"""
        Analyze the following {content_type} content for inappropriate language, hate speech, spam, or other violations.
        
        Content: "{content}"
        
        Please respond with a JSON object containing:
        {{
            "is_appropriate": true/false,
            "confidence": 0.0-1.0,
            "issues": ["list", "of", "issues"],
            "severity": "low/medium/high"
        }}
        
        Consider:
        - Profanity and offensive language
        - Hate speech or discrimination
        - Spam or promotional content
        - Threats or harassment
        - Inappropriate content for general audience
        
        Respond only with the JSON object, no additional text.
        """
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from Google AI"""
        if not self.model:
            raise Exception("Google AI model not configured")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self._call_ai_sync, prompt)
        return response
    
    def _call_ai_sync(self, prompt: str) -> str:
        """Synchronous call to Google AI"""
        response = self.model.generate_content(prompt)
        return response.text
    
    def _parse_moderation_response(self, response: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Extract JSON from response
            import json
            import re
            
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback parsing
                result = self._fallback_parsing(response)
            
            # Ensure required fields
            result.setdefault("is_appropriate", True)
            result.setdefault("confidence", 0.5)
            result.setdefault("issues", [])
            result.setdefault("severity", "low")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing moderation response: {e}")
            return {
                "is_appropriate": True,
                "confidence": 0.5,
                "issues": ["Parsing error"],
                "severity": "low"
            }
    
    def _fallback_parsing(self, response: str) -> Dict:
        """Fallback parsing if JSON parsing fails"""
        response_lower = response.lower()
        
        # Simple keyword-based fallback
        inappropriate_keywords = ["inappropriate", "violation", "block", "reject"]
        appropriate_keywords = ["appropriate", "acceptable", "pass", "allow"]
        
        is_appropriate = any(word in response_lower for word in appropriate_keywords)
        if any(word in response_lower for word in inappropriate_keywords):
            is_appropriate = False
        
        return {
            "is_appropriate": is_appropriate,
            "confidence": 0.3,
            "issues": ["Fallback moderation used"],
            "severity": "low"
        }


class AutoReplyService:
    """Service for generating automatic replies to comments"""
    
    def __init__(self):
        self.model = model
        self.enabled = settings.AUTO_REPLY_ENABLED and self.model is not None
    
    async def generate_reply(self, post_content: str, comment_content: str, post_title: str = "") -> str:
        """
        Generate automatic reply to a comment
        
        Args:
            post_content: Original post content
            comment_content: Comment to reply to
            post_title: Post title (optional)
            
        Returns:
            Generated reply text
        """
        if not self.enabled:
            return ""
        
        try:
            prompt = self._create_reply_prompt(post_content, comment_content, post_title)
            response = await self._get_ai_response(prompt)
            
            # Clean up response
            reply = self._clean_reply(response)
            
            logger.info(f"Auto-reply generated: {reply[:100]}...")
            return reply
            
        except Exception as e:
            logger.error(f"Error generating auto-reply: {e}")
            return ""
    
    def _create_reply_prompt(self, post_content: str, comment_content: str, post_title: str) -> str:
        """Create prompt for generating reply"""
        return f"""
        Generate a helpful and relevant reply to this comment on a blog post.
        
        Post Title: {post_title}
        Post Content: {post_content}
        Comment: {comment_content}
        
        Requirements:
        - Be helpful and informative
        - Address the comment's content directly
        - Keep it concise (1-2 sentences)
        - Be friendly and professional
        - Don't be overly promotional
        - If the comment is negative, be constructive
        
        Generate only the reply text, no additional formatting or explanations.
        """
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from Google AI"""
        if not self.model:
            raise Exception("Google AI model not configured")
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self._call_ai_sync, prompt)
        return response
    
    def _call_ai_sync(self, prompt: str) -> str:
        """Synchronous call to Google AI"""
        response = self.model.generate_content(prompt)
        return response.text
    
    def _clean_reply(self, reply: str) -> str:
        """Clean up the generated reply"""
        # Remove quotes and extra formatting
        reply = reply.strip()
        reply = reply.strip('"')
        reply = reply.strip("'")
        
        # Limit length
        if len(reply) > 500:
            reply = reply[:497] + "..."
        
        return reply


# Global service instances
content_moderation = ContentModerationService()
auto_reply = AutoReplyService()
