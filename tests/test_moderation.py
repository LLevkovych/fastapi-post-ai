import pytest
from unittest.mock import patch, AsyncMock
from app.services.content_moderation import moderate_content, ModerationResult

class TestContentModeration:
    """Test content moderation functionality"""
    
    @pytest.mark.asyncio
    async def test_moderate_content_appropriate(self):
        """Test moderation of appropriate content"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "flagged": False,
                "confidence": 0.95,
                "issues": [],
                "severity": "none"
            }
            mock_client.post.return_value = mock_response
            
            result = await moderate_content("This is a nice, appropriate comment.")
            
            assert isinstance(result, ModerationResult)
            assert result.is_appropriate == True
            assert result.confidence == 0.95
            assert result.issues == []
            assert result.severity == "none"
    
    @pytest.mark.asyncio
    async def test_moderate_content_inappropriate(self):
        """Test moderation of inappropriate content"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "flagged": True,
                "confidence": 0.88,
                "issues": ["profanity", "hate_speech"],
                "severity": "high"
            }
            mock_client.post.return_value = mock_response
            
            result = await moderate_content("This contains bad words and hate speech.")
            
            assert isinstance(result, ModerationResult)
            assert result.is_appropriate == False
            assert result.confidence == 0.88
            assert "profanity" in result.issues
            assert "hate_speech" in result.issues
            assert result.severity == "high"
    
    @pytest.mark.asyncio
    async def test_moderate_content_no_api_key(self):
        """Test moderation when no API key is provided"""
        with patch('app.config.settings.GOOGLE_AI_API_KEY', None):
            result = await moderate_content("Any content")
            
            assert isinstance(result, ModerationResult)
            assert result.is_appropriate == True
            assert result.confidence == 1.0
            assert result.issues == []
            assert result.severity == "none"
    
    @pytest.mark.asyncio
    async def test_moderate_content_api_error(self):
        """Test moderation when API returns an error"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = Exception("API Error")
            
            result = await moderate_content("Any content")
            
            assert isinstance(result, ModerationResult)
            assert result.is_appropriate == True  # Fallback to allow
            assert result.confidence == 0.5
            assert "moderation_error" in result.issues
            assert result.severity == "unknown"
    
    @pytest.mark.asyncio
    async def test_moderation_result_to_dict(self):
        """Test ModerationResult to_dict method"""
        result = ModerationResult(
            is_appropriate=False,
            confidence=0.75,
            issues=["spam"],
            severity="medium"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["is_appropriate"] == False
        assert result_dict["confidence"] == 0.75
        assert result_dict["issues"] == ["spam"]
        assert result_dict["severity"] == "medium" 