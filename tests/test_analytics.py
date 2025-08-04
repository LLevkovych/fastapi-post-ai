import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from app.models import Comment, Post, User
from app.utils import get_password_hash


class TestAnalytics:
    """Test analytics functionality"""
    
    def test_comments_daily_breakdown_success(self, client, auth_headers, db_session):
        """Test successful analytics retrieval"""
        # Create test data
        user = User(
            email="analytics@test.com",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        post = Post(
            title="Analytics Test Post",
            content="Test content",
            author_id=user.id,
            auto_reply_enabled=False
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        
        # Create comments for different dates
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Today's comments
        comment1 = Comment(
            content="Comment 1",
            author_id=user.id,
            post_id=post.id,
            created_at=datetime.combine(today, datetime.min.time()),
            is_blocked=False
        )
        comment2 = Comment(
            content="Comment 2",
            author_id=user.id,
            post_id=post.id,
            created_at=datetime.combine(today, datetime.min.time()),
            is_blocked=True  # Blocked comment
        )
        
        # Yesterday's comments
        comment3 = Comment(
            content="Comment 3",
            author_id=user.id,
            post_id=post.id,
            created_at=datetime.combine(yesterday, datetime.min.time()),
            is_blocked=False
        )
        
        db_session.add_all([comment1, comment2, comment3])
        db_session.commit()
        
        # Test analytics endpoint
        date_from = yesterday
        date_to = today
        
        response = client.get(
            f"/api/comments-daily-breakdown?date_from={date_from}&date_to={date_to}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "period" in data
        assert "data" in data
        assert "summary" in data
        
        # Check summary statistics
        summary = data["summary"]
        assert summary["total_comments"] == 3
        assert summary["total_blocked"] == 1
        assert summary["total_active"] == 2
        assert summary["blocked_percentage"] == 33.33
        assert summary["period_days"] == 2
        
        # Check daily breakdown
        daily_data = data["data"]
        assert len(daily_data) == 2
        
        # Find today's data
        today_data = next((item for item in daily_data if item["date"] == str(today)), None)
        assert today_data is not None
        assert today_data["total_comments"] == 2
        assert today_data["blocked_comments"] == 1
        assert today_data["active_comments"] == 1
        
        # Find yesterday's data
        yesterday_data = next((item for item in daily_data if item["date"] == str(yesterday)), None)
        assert yesterday_data is not None
        assert yesterday_data["total_comments"] == 1
        assert yesterday_data["blocked_comments"] == 0
        assert yesterday_data["active_comments"] == 1
    
    def test_comments_daily_breakdown_invalid_dates(self, client, auth_headers):
        """Test analytics with invalid date range"""
        # Test with date_from > date_to
        date_from = date.today()
        date_to = date_from - timedelta(days=1)
        
        response = client.get(
            f"/api/comments-daily-breakdown?date_from={date_from}&date_to={date_to}",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "date_from cannot be later than date_to" in data["detail"]
    
    def test_comments_daily_breakdown_too_large_range(self, client, auth_headers):
        """Test analytics with date range exceeding 365 days"""
        date_from = date.today() - timedelta(days=400)
        date_to = date.today()
        
        response = client.get(
            f"/api/comments-daily-breakdown?date_from={date_from}&date_to={date_to}",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Date range cannot exceed 365 days" in data["detail"]
    
    def test_comments_daily_breakdown_no_data(self, client, auth_headers):
        """Test analytics when no comments exist in date range"""
        date_from = date.today() - timedelta(days=10)
        date_to = date.today() - timedelta(days=5)
        
        response = client.get(
            f"/api/comments-daily-breakdown?date_from={date_from}&date_to={date_to}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty data but valid structure
        assert data["summary"]["total_comments"] == 0
        assert data["summary"]["total_blocked"] == 0
        assert data["summary"]["total_active"] == 0
        assert len(data["data"]) == 0
    
    def test_comments_last_30_days(self, client, auth_headers, db_session):
        """Test last 30 days analytics endpoint"""
        # Create test data
        user = User(
            email="last30@test.com",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        post = Post(
            title="Last 30 Days Test",
            content="Test content",
            author_id=user.id,
            auto_reply_enabled=False
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        
        # Create a comment from today
        comment = Comment(
            content="Recent comment",
            author_id=user.id,
            post_id=post.id,
            created_at=datetime.now(),
            is_blocked=False
        )
        db_session.add(comment)
        db_session.commit()
        
        response = client.get("/api/comments-daily-breakdown/last-30-days", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that it covers 30 days
        assert data["summary"]["period_days"] == 30
        assert data["summary"]["total_comments"] >= 1
    
    def test_comments_last_7_days(self, client, auth_headers, db_session):
        """Test last 7 days analytics endpoint"""
        # Create test data
        user = User(
            email="last7@test.com",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        post = Post(
            title="Last 7 Days Test",
            content="Test content",
            author_id=user.id,
            auto_reply_enabled=False
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        
        # Create a comment from today
        comment = Comment(
            content="Recent comment",
            author_id=user.id,
            post_id=post.id,
            created_at=datetime.now(),
            is_blocked=False
        )
        db_session.add(comment)
        db_session.commit()
        
        response = client.get("/api/comments-daily-breakdown/last-7-days", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that it covers 7 days
        assert data["summary"]["period_days"] == 7
        assert data["summary"]["total_comments"] >= 1
    
    def test_analytics_unauthorized(self, client):
        """Test analytics without authentication"""
        date_from = date.today() - timedelta(days=7)
        date_to = date.today()
        
        response = client.get(
            f"/api/comments-daily-breakdown?date_from={date_from}&date_to={date_to}"
        )
        
        assert response.status_code == 401
    
    def test_analytics_with_mixed_comment_types(self, client, auth_headers, db_session):
        """Test analytics with regular and auto-reply comments"""
        # Create test data
        user = User(
            email="mixed@test.com",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        post = Post(
            title="Mixed Comments Test",
            content="Test content",
            author_id=user.id,
            auto_reply_enabled=True
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        
        today = date.today()
        
        # Regular comment
        regular_comment = Comment(
            content="Regular comment",
            author_id=user.id,
            post_id=post.id,
            created_at=datetime.combine(today, datetime.min.time()),
            is_blocked=False,
            is_auto_reply=False
        )
        
        # Auto-reply comment
        auto_reply_comment = Comment(
            content="Auto-reply comment",
            author_id=user.id,
            post_id=post.id,
            created_at=datetime.combine(today, datetime.min.time()),
            is_blocked=False,
            is_auto_reply=True
        )
        
        # Blocked comment
        blocked_comment = Comment(
            content="Blocked comment",
            author_id=user.id,
            post_id=post.id,
            created_at=datetime.combine(today, datetime.min.time()),
            is_blocked=True,
            is_auto_reply=False
        )
        
        db_session.add_all([regular_comment, auto_reply_comment, blocked_comment])
        db_session.commit()
        
        # Test analytics
        response = client.get(
            f"/api/comments-daily-breakdown?date_from={today}&date_to={today}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All comments should be counted regardless of type
        assert data["summary"]["total_comments"] == 3
        assert data["summary"]["total_blocked"] == 1
        assert data["summary"]["total_active"] == 2 