import requests
import json

BASE_URL = "http://localhost:8001"

def test_basic_functionality():
    """Test basic API functionality"""
    print("=== FastPostAI Basic Functionality Test ===\n")
    
    # Test 1: Health check
    print("1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed")
    
    # Test 2: User registration
    print("\n2. Testing user registration...")
    register_data = {
        "email": "test_basic@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 201:
        print("✅ User registration passed")
    elif response.status_code == 400 and "already registered" in response.text:
        print("✅ User already exists (expected)")
    else:
        print(f"❌ User registration failed: {response.status_code} - {response.text}")
        return False
    
    # Test 3: User login
    print("\n3. Testing user login...")
    login_data = {
        "email": "test_basic@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]
    print("✅ User login passed")
    
    # Test 4: Create post
    print("\n4. Testing post creation...")
    headers = {"Authorization": f"Bearer {token}"}
    post_data = {
        "title": "Basic Test Post",
        "content": "This is a basic test post for functionality testing.",
        "auto_reply_enabled": True,
        "auto_reply_delay": 30
    }
    response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    post_id = data["id"]
    print(f"✅ Post creation passed (ID: {post_id})")
    
    # Test 5: Create comment
    print("\n5. Testing comment creation...")
    comment_data = {
        "content": "This is a test comment for functionality testing."
    }
    response = requests.post(f"{BASE_URL}/posts/{post_id}/comments/", json=comment_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    comment_id = data["id"]
    print(f"✅ Comment creation passed (ID: {comment_id})")
    
    # Test 6: Get comments
    print("\n6. Testing get comments...")
    response = requests.get(f"{BASE_URL}/posts/{post_id}/comments/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    print(f"✅ Get comments passed (found {data['total']} comments)")
    
    # Test 7: Get posts
    print("\n7. Testing get posts...")
    response = requests.get(f"{BASE_URL}/posts/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    print(f"✅ Get posts passed (found {data['total']} posts)")
    
    print("\n=== All basic functionality tests passed! ===")
    return True

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1) 