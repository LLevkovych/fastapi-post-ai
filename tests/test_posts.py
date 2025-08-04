import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.services import content_moderation


class TestPostCreation:
    """Test post creation with AI moderation"""
    
    def test_create_post_success(self, client, auth_headers):
        """Test successful post creation with appropriate content"""
        with patch.object(content_moderation, 'moderate_content', new_callable=AsyncMock) as mock_moderate:
            # Mock AI moderation to allow content
            mock_moderate.return_value = {
                "is_appropriate": True,
                "confidence": 0.9,
                "issues": [],
                "severity": "low"
            }
            
            post_data = {
                "title": "Test Post Title",
                "content": "This is a test post with appropriate content.",
                "auto_reply_enabled": True,
                "auto_reply_delay": 120
            }
            
            response = client.post("/posts/", json=post_data, headers=auth_headers)
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == post_data["title"]
            assert data["content"] == post_data["content"]
            assert data["auto_reply_enabled"] == post_data["auto_reply_enabled"]
            assert data["auto_reply_delay"] == post_data["auto_reply_delay"]
            
            # Verify moderation was called
            mock_moderate.assert_called_once()
    
    def test_create_post_inappropriate_content(self, client, auth_headers):
        """Test post creation with inappropriate content"""
        with patch.object(content_moderation, 'moderate_content', new_callable=AsyncMock) as mock_moderate:
            # Mock AI moderation to block content
            mock_moderate.return_value = {
                "is_appropriate": False,
                "confidence": 0.8,
                "issues": ["profanity", "hate speech"],
                "severity": "high"
            }
            
            post_data = {
                "title": "Inappropriate Post",
                "content": "This post contains inappropriate content.",
                "auto_reply_enabled": False,
                "auto_reply_delay": 60
            }
            
            response = client.post("/posts/", json=post_data, headers=auth_headers)
            
            assert response.status_code == 400
            data = response.json()
            assert "inappropriate content" in data["detail"]["message"]
            assert "profanity" in data["detail"]["issues"]
            assert data["detail"]["severity"] == "high"
    
    def test_create_post_moderation_service_unavailable(self, client, auth_headers):
        """Test post creation when moderation service is unavailable"""
        with patch.object(content_moderation, 'moderate_content', new_callable=AsyncMock) as mock_moderate:
            # Mock AI moderation to fail
            mock_moderate.side_effect = Exception("Service unavailable")
            
            post_data = {
                "title": "Test Post",
                "content": "This is a test post.",
                "auto_reply_enabled": False,
                "auto_reply_delay": 60
            }
            
            response = client.post("/posts/", json=post_data, headers=auth_headers)
            
            # Should still succeed due to fallback behavior
            assert response.status_code == 201
    
    def test_create_post_unauthorized(self, client):
        """Test post creation without authentication"""
        post_data = {
            "title": "Test Post",
            "content": "This is a test post.",
            "auto_reply_enabled": False,
            "auto_reply_delay": 60
        }
        
        response = client.post("/posts/", json=post_data)
        
        assert response.status_code == 401
    
    def test_create_post_invalid_data(self, client, auth_headers):
        """Test post creation with invalid data"""
        with patch.object(content_moderation, 'moderate_content', new_callable=AsyncMock) as mock_moderate:
            mock_moderate.return_value = {
                "is_appropriate": True,
                "confidence": 0.9,
                "issues": [],
                "severity": "low"
            }
            
            # Missing required fields
            post_data = {
                "title": "",  # Empty title
                "content": "This is content."
            }
            
            response = client.post("/posts/", json=post_data, headers=auth_headers)
            
            assert response.status_code == 422
    
    def test_create_post_with_moderation_disabled(self, client, auth_headers):
        """Test post creation when moderation is disabled"""
        # Temporarily disable moderation
        original_enabled = content_moderation.moderation_enabled
        content_moderation.moderation_enabled = False
        
        try:
            post_data = {
                "title": "Test Post",
                "content": "This is a test post.",
                "auto_reply_enabled": True,
                "auto_reply_delay": 60
            }
            
            response = client.post("/posts/", json=post_data, headers=auth_headers)
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == post_data["title"]
            
        finally:
            # Restore moderation setting
            content_moderation.moderation_enabled = original_enabled


class TestPostRetrieval:
    """Test post retrieval functionality"""
    
    def test_get_posts_list(self, client, auth_headers, test_post):
        """Test getting list of posts"""
        response = client.get("/posts/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "total" in data
        assert "page" in data
        assert len(data["posts"]) >= 1
    
    def test_get_post_by_id(self, client, auth_headers, test_post):
        """Test getting a specific post by ID"""
        response = client.get(f"/posts/{test_post.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_post.id
        assert data["title"] == test_post.title
        assert data["content"] == test_post.content
    
    def test_get_nonexistent_post(self, client, auth_headers):
        """Test getting a post that doesn't exist"""
        response = client.get("/posts/99999", headers=auth_headers)
        
        assert response.status_code == 404


class TestPostUpdate:
    """Test post update functionality"""
    
    def test_update_post_success(self, client, auth_headers, test_post):
        """Test successful post update"""
        with patch.object(content_moderation, 'moderate_content', new_callable=AsyncMock) as mock_moderate:
            mock_moderate.return_value = {
                "is_appropriate": True,
                "confidence": 0.9,
                "issues": [],
                "severity": "low"
            }
            
            update_data = {
                "title": "Updated Post Title",
                "content": "This is updated content.",
                "auto_reply_enabled": False,
                "auto_reply_delay": 30
            }
            
            response = client.put(f"/posts/{test_post.id}", json=update_data, headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == update_data["title"]
            assert data["content"] == update_data["content"]
    
    def test_update_post_inappropriate_content(self, client, auth_headers, test_post):
        """Test post update with inappropriate content"""
        with patch.object(content_moderation, 'moderate_content', new_callable=AsyncMock) as mock_moderate:
            mock_moderate.return_value = {
                "is_appropriate": False,
                "confidence": 0.8,
                "issues": ["spam"],
                "severity": "medium"
            }
            
            update_data = {
                "title": "Updated Post",
                "content": "This contains spam content.",
                "auto_reply_enabled": True,
                "auto_reply_delay": 60
            }
            
            response = client.put(f"/posts/{test_post.id}", json=update_data, headers=auth_headers)
            
            assert response.status_code == 400
            data = response.json()
            assert "inappropriate content" in data["detail"]["message"]


class TestPostDeletion:
    """Test post deletion functionality"""
    
    def test_delete_post_success(self, client, auth_headers, test_post):
        """Test successful post deletion"""
        response = client.delete(f"/posts/{test_post.id}", headers=auth_headers)
        
        assert response.status_code == 204
    
    def test_delete_nonexistent_post(self, client, auth_headers):
        """Test deleting a post that doesn't exist"""
        response = client.delete("/posts/99999", headers=auth_headers)
        
        assert response.status_code == 404 