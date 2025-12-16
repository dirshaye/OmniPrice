import subprocess
import time
import requests
import sys
import os
import signal

def run_verification():
    print("🚀 Starting server...")
    # Start uvicorn in a separate process
    process = subprocess.Popen(
        ["uvicorn", "omniprice.main:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid # Create a new session group
    )
    
    try:
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Test Health Check (Root)
        try:
            response = requests.get("http://localhost:8000/")
            print(f"✅ Root endpoint: {response.status_code}")
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")

        # Test Registration
        print("👤 Testing Registration...")
        user_data = {
            "email": "verify_user@example.com",
            "password": "securepassword123",
            "full_name": "Verification User"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=user_data
        )
        
        if response.status_code == 201:
            print(f"✅ Registration successful: {response.json()}")
        elif response.status_code == 400 and "already exists" in response.text:
             print(f"✅ User already exists (Test passed previously)")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")

        # Test Login
        print("🔑 Testing Login...")
        login_data = {
            "username": "verify_user@example.com", # OAuth2 form uses 'username' for email
            "password": "securepassword123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data
        )
        
        if response.status_code == 200:
            token = response.json()
            print(f"✅ Login successful. Token: {token['access_token'][:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")

    finally:
        print("🛑 Stopping server...")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        # process.terminate()
        # process.wait()

if __name__ == "__main__":
    run_verification()
