#!/usr/bin/env python3
"""
Demo script showing how to use the Auth Service API
Run this after starting the auth service to test functionality
"""
import requests
import json
import time

# Auth service base URL
BASE_URL = "http://localhost:8001/api/v1"

def demo_auth_flow():
    """Demonstrate complete authentication flow"""
    
    print("🚀 OmniPriceX Auth Service Demo")
    print("=" * 50)
    
    # Test data
    user_data = {
        "email": "demo@omnipricex.com",
        "username": "demouser",
        "full_name": "Demo User",
        "password": "demopassword123",
        "company_name": "OmniPriceX Demo"
    }
    
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        # 1. Health Check
        print("1️⃣ Testing health check...")
        response = requests.get(f"{BASE_URL}/auth/health")
        if response.status_code == 200:
            print("   ✅ Auth service is healthy!")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
        
        # 2. Register User
        print("\n2️⃣ Registering new user...")
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            user_info = response.json()
            print(f"   ✅ User registered successfully!")
            print(f"   📧 Email: {user_info['email']}")
            print(f"   👤 Username: {user_info['username']}")
            print(f"   🏢 Company: {user_info['company_name']}")
        elif response.status_code == 400:
            print("   ⚠️ User already exists (continuing with login)")
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
        
        # 3. Login User
        print("\n3️⃣ Logging in user...")
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
            user_info = tokens["user"]
            
            print("   ✅ Login successful!")
            print(f"   🔑 Access token: {access_token[:30]}...")
            print(f"   🔄 Refresh token: {refresh_token[:30]}...")
            print(f"   ⏰ Expires in: {tokens['expires_in']} seconds")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
        
        # 4. Get Current User Info
        print("\n4️⃣ Getting current user info...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print("   ✅ User info retrieved!")
            print(f"   📧 Email: {user_info['email']}")
            print(f"   👤 Role: {user_info['role']}")
            print(f"   ✅ Active: {user_info['is_active']}")
            print(f"   📅 Created: {user_info['created_at']}")
        else:
            print(f"   ❌ Failed to get user info: {response.status_code}")
        
        # 5. Verify Token
        print("\n5️⃣ Verifying access token...")
        response = requests.post(f"{BASE_URL}/auth/verify-token", json={"token": access_token})
        if response.status_code == 200:
            token_info = response.json()
            print("   ✅ Token is valid!")
            print(f"   👤 User ID: {token_info['user_id']}")
            print(f"   📧 Email: {token_info['email']}")
            print(f"   🎭 Role: {token_info['role']}")
        else:
            print(f"   ❌ Token verification failed: {response.status_code}")
        
        # 6. Refresh Token
        print("\n6️⃣ Refreshing access token...")
        response = requests.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh_token})
        if response.status_code == 200:
            new_tokens = response.json()
            new_access_token = new_tokens["access_token"]
            print("   ✅ Token refreshed successfully!")
            print(f"   🔑 New access token: {new_access_token[:30]}...")
        else:
            print(f"   ❌ Token refresh failed: {response.status_code}")
            new_access_token = access_token  # Keep old token for logout
        
        # 7. Logout
        print("\n7️⃣ Logging out user...")
        headers = {"Authorization": f"Bearer {new_access_token}"}
        response = requests.post(f"{BASE_URL}/auth/logout", 
                               json={"refresh_token": refresh_token}, 
                               headers=headers)
        if response.status_code == 200:
            print("   ✅ Logout successful!")
        else:
            print(f"   ❌ Logout failed: {response.status_code}")
        
        print("\n🎉 Auth service demo completed successfully!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to auth service!")
        print("Make sure the service is running on http://localhost:8001")
        print("Run: python run.py")
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")

def show_api_info():
    """Show API endpoint information"""
    print("\n📋 Auth Service API Endpoints:")
    print("=" * 30)
    endpoints = [
        ("POST", "/auth/register", "Register new user"),
        ("POST", "/auth/login", "Login user"),
        ("POST", "/auth/refresh", "Refresh access token"),
        ("POST", "/auth/logout", "Logout user"),
        ("GET", "/auth/me", "Get current user info"),
        ("POST", "/auth/verify-token", "Verify token"),
        ("GET", "/auth/health", "Health check"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"{method:6} {BASE_URL}{endpoint:20} - {description}")
    
    print(f"\n📖 API Documentation: http://localhost:8001/api/v1/docs")
    print(f"🔍 Alternative Docs: http://localhost:8001/api/v1/redoc")

if __name__ == "__main__":
    show_api_info()
    print("\nStarting demo in 3 seconds...")
    time.sleep(3)
    demo_auth_flow()
