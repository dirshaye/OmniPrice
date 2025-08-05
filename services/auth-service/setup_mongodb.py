#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test Script
Run this script to verify your MongoDB Atlas connection
"""
import asyncio
import motor.motor_asyncio
from beanie import init_beanie
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    
    print("🔗 Testing MongoDB Atlas Connection...")
    print("=" * 50)
    
    # Get connection string from environment
    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME", "omnipricex_auth")
    
    if not mongodb_url or mongodb_url == "mongodb+srv://your-username:your-password@your-cluster.xxxxx.mongodb.net/omnipricex_auth?retryWrites=true&w=majority":
        print("❌ MongoDB connection string not configured!")
        print("\n📋 Setup Instructions:")
        print("1. Go to https://www.mongodb.com/atlas")
        print("2. Create account and cluster")
        print("3. Create database user")
        print("4. Whitelist IP address")
        print("5. Get connection string")
        print("6. Update MONGODB_URL in .env file")
        return False
    
    try:
        # Test basic connection
        print(f"🔗 Connecting to: {mongodb_url.split('@')[1] if '@' in mongodb_url else 'MongoDB Atlas'}")
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        
        # Test ping
        await client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Test database access
        database = client[database_name]
        print(f"📊 Database: {database_name}")
        
        # List collections
        collections = await database.list_collection_names()
        print(f"📁 Collections: {collections if collections else 'None (new database)'}")
        
        # Test write operation
        test_collection = database.test_connection
        result = await test_collection.insert_one({"test": "connection", "timestamp": "2025-08-03"})
        print(f"✅ Write test successful! Document ID: {result.inserted_id}")
        
        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        # Close connection
        client.close()
        print("✅ MongoDB Atlas connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n🔧 Common Issues:")
        print("1. Check username/password in connection string")
        print("2. Verify IP address is whitelisted")
        print("3. Ensure cluster is running")
        print("4. Check network connectivity")
        return False

async def test_beanie_initialization():
    """Test Beanie ODM initialization"""
    
    print("\n🔧 Testing Beanie ODM Setup...")
    print("=" * 30)
    
    try:
        from app.models import User, RefreshToken
        
        mongodb_url = os.getenv("MONGODB_URL")
        database_name = os.getenv("DATABASE_NAME", "omnipricex_auth")
        
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        database = client[database_name]
        
        # Initialize Beanie
        await init_beanie(database=database, document_models=[User, RefreshToken])
        print("✅ Beanie initialization successful!")
        
        # Test User model
        print("📝 Testing User model...")
        user_count = await User.count()
        print(f"👥 Current users in database: {user_count}")
        
        # Test RefreshToken model
        print("🔑 Testing RefreshToken model...")
        token_count = await RefreshToken.count()
        print(f"🎫 Current tokens in database: {token_count}")
        
        client.close()
        print("✅ Models test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Beanie setup failed: {str(e)}")
        return False

def show_atlas_setup_guide():
    """Show step-by-step MongoDB Atlas setup guide"""
    
    print("\n📚 MongoDB Atlas Setup Guide")
    print("=" * 40)
    
    steps = [
        ("1️⃣ Create Account", "Go to https://www.mongodb.com/atlas and sign up"),
        ("2️⃣ Create Cluster", "Choose M0 Sandbox (free tier) and create cluster"),
        ("3️⃣ Database Access", "Create database user with username/password"),
        ("4️⃣ Network Access", "Add IP address (0.0.0.0/0 for development)"),
        ("5️⃣ Get Connection String", "Click 'Connect' → 'Connect your application'"),
        ("6️⃣ Update .env", "Replace MONGODB_URL in .env file"),
        ("7️⃣ Test Connection", "Run this script to verify connection"),
    ]
    
    for step, description in steps:
        print(f"{step} {description}")
    
    print(f"\n🔗 Example connection string format:")
    print("mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/omnipricex_auth?retryWrites=true&w=majority")
    
    print(f"\n⚠️ Security Notes:")
    print("- Use strong passwords for database users")
    print("- Restrict IP access in production")
    print("- Keep connection strings secure")

async def main():
    """Main test function"""
    
    print("🚀 OmniPriceX Auth Service - MongoDB Atlas Setup")
    print("=" * 60)
    
    # Show setup guide
    show_atlas_setup_guide()
    
    # Test connection
    connection_ok = await test_mongodb_connection()
    
    if connection_ok:
        # Test Beanie setup
        await test_beanie_initialization()
        print("\n🎉 All tests passed! Your MongoDB Atlas is ready!")
        print("You can now start the auth service with: python run.py")
    else:
        print("\n⚠️ Please fix MongoDB connection issues before starting the service")

if __name__ == "__main__":
    asyncio.run(main())
