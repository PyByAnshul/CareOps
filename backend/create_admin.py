"""
Script to create an admin user.

Run the server first:
    uvicorn app.main:app --reload

Then run this script:
    python create_admin.py
"""

import requests

BASE_URL = "http://localhost:8000"

def create_admin_user():
    print("Creating admin user...")
    
    # Register admin user with 'owner' role
    admin_data = {
        "email": "admin@careops.com",
        "password": "admin123",
        "workspace_id": 1,
        "role": "owner"  # This makes the user an admin
    }
    
    response = requests.post(f"{BASE_URL}/api/users/register", json=admin_data)
    
    if response.status_code == 201:
        print("✓ Admin user created successfully!")
        print(f"  Email: {admin_data['email']}")
        print(f"  Password: {admin_data['password']}")
        print(f"  Role: {admin_data['role']}")
        print("\nYou can now login with these credentials.")
    else:
        print(f"✗ Failed to create admin user: {response.json()}")
        if "already registered" in response.json().get("detail", ""):
            print("Admin user already exists!")

if __name__ == "__main__":
    try:
        create_admin_user()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server.")
        print("Make sure the server is running: uvicorn app.main:app --reload")