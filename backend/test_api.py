#!/usr/bin/env python3
"""
Test script to check if forms API is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_forms_api():
    print("Testing Forms API...")
    
    # 1. Login first
    print("1. Logging in...")
    login_data = {
        "email": "admin@careops.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/users/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return
    
    token = response.json()["access_token"]
    print("✅ Login successful")
    
    # 2. Test forms list endpoint
    print("2. Testing forms list...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/forms", headers=headers)
    print(f"Forms API Response: {response.status_code}")
    
    if response.status_code == 200:
        forms = response.json()
        print(f"✅ Found {len(forms)} forms")
        for form in forms:
            print(f"  - {form['name']} (ID: {form['id']})")
    else:
        print(f"❌ Forms API failed: {response.status_code} - {response.text}")
    
    # 3. Test other endpoints
    print("3. Testing other endpoints...")
    endpoints = [
        "/api/users/me",
        "/api/bookings", 
        "/api/services",
        "/api/contacts"
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"  {status} {endpoint}: {response.status_code}")

if __name__ == "__main__":
    try:
        test_forms_api()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure backend is running on http://localhost:8000")