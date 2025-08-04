#!/usr/bin/env python3
"""
Quick API testing script for FastPostAI
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_response(response: requests.Response, title: str):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")

def test_api():
    """Test main API endpoints"""
    
    print("🚀 Starting FastPostAI API Tests")
    print(f"Base URL: {BASE_URL}")
    
    # Test 1: Root endpoint
    print("\n1️⃣ Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "Root Endpoint")
    
    # Test 2: Health check
    print("\n2️⃣ Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    
    # Test 3: Register user
    print("\n3️⃣ Testing user registration...")
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print_response(response, "User Registration")
    
    if response.status_code == 201:
        user = response.json()
        print(f"✅ User created with ID: {user.get('id')}")
    else:
        print("⚠️ User might already exist or registration failed")
    
    # Test 4: Login
    print("\n4️⃣ Testing user login...")
    response = requests.post(f"{BASE_URL}/auth/login", json=user_data)
    print_response(response, "User Login")
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get("access_token")
        print(f"✅ Login successful, got access token")
        
        # Test 5: Create post
        print("\n5️⃣ Testing post creation...")
        headers = {"Authorization": f"Bearer {access_token}"}
        post_data = {
            "title": "Test Post",
            "content": "This is a test post content",
            "auto_reply_enabled": True,
            "auto_reply_delay": 60
        }
        response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=headers)
        print_response(response, "Post Creation")
        
        if response.status_code == 201:
            post = response.json()
            post_id = post.get("id")
            print(f"✅ Post created with ID: {post_id}")
            
            # Test 6: Create comment
            print("\n6️⃣ Testing comment creation...")
            comment_data = {
                "content": "Great post! Thanks for sharing."
            }
            response = requests.post(
                f"{BASE_URL}/posts/{post_id}/comments/", 
                json=comment_data, 
                headers=headers
            )
            print_response(response, "Comment Creation")
            
            if response.status_code == 201:
                comment = response.json()
                comment_id = comment.get("id")
                print(f"✅ Comment created with ID: {comment_id}")
                
                # Test 7: Get comments
                print("\n7️⃣ Testing get comments...")
                response = requests.get(f"{BASE_URL}/posts/{post_id}/comments/")
                print_response(response, "Get Comments")
                
                # Test 8: Get posts
                print("\n8️⃣ Testing get posts...")
                response = requests.get(f"{BASE_URL}/posts/")
                print_response(response, "Get Posts")
                
                # Test 9: Analytics (if user is authenticated)
                print("\n9️⃣ Testing analytics...")
                response = requests.get(
                    f"{BASE_URL}/api/comments-daily-breakdown/last-7-days",
                    headers=headers
                )
                print_response(response, "Analytics")
        
    else:
        print("❌ Login failed, skipping authenticated tests")
    
    # Test 10: Error handling
    print("\n🔟 Testing error handling...")
    response = requests.get(f"{BASE_URL}/nonexistent-endpoint")
    print_response(response, "404 Error Handling")
    
    print(f"\n{'='*50}")
    print("🎉 API Testing Complete!")
    print(f"{'='*50}")
    print("\n📚 Next steps:")
    print("1. Open http://localhost:8000/docs for interactive documentation")
    print("2. Check API_INFO.md for detailed endpoint information")
    print("3. Use TESTING.md for more testing examples")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
        print("💡 Start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}") 