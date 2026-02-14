"""
Test script for authentication flow.

Run the server first:
    uvicorn app.main:app --reload

Then run this script:
    python test_auth.py
"""

import requests

BASE_URL = "http://localhost:8000"


def test_auth_flow():
    print("=" * 60)
    print("Testing CareOps Authentication Flow")
    print("=" * 60)
    
    # 1. Register a new user
    print("\n1. Registering new user...")
    register_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "workspace_id": 1,
        "role": "owner"
    }
    
    response = requests.post(f"{BASE_URL}/api/users/register", json=register_data)
    if response.status_code == 201:
        print("✓ User registered successfully")
        print(f"  User ID: {response.json()['id']}")
        print(f"  Email: {response.json()['email']}")
    else:
        print(f"✗ Registration failed: {response.json()}")
        if "already registered" in response.json().get("detail", ""):
            print("  (User already exists, continuing with login...)")
    
    # 2. Login
    print("\n2. Logging in...")
    login_data = {
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/users/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✓ Login successful")
        print(f"  Token: {token[:50]}...")
    else:
        print(f"✗ Login failed: {response.json()}")
        return
    
    # 3. Get current user info
    print("\n3. Getting current user info...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print("✓ User info retrieved successfully")
        print(f"  ID: {user_info['id']}")
        print(f"  Email: {user_info['email']}")
        print(f"  Role: {user_info['role']}")
        print(f"  Workspace ID: {user_info['workspace_id']}")
        print(f"  Active: {user_info['is_active']}")
    else:
        print(f"✗ Failed to get user info: {response.json()}")
    
    # 4. Test with invalid token
    print("\n4. Testing with invalid token...")
    headers = {"Authorization": "Bearer invalid_token_here"}
    
    response = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
    if response.status_code == 401:
        print("✓ Invalid token correctly rejected")
    else:
        print(f"✗ Unexpected response: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("Authentication flow test completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server.")
        print("Make sure the server is running: uvicorn app.main:app --reload")
