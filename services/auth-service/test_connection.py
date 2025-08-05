#!/usr/bin/env python3
"""
Simple MongoDB Atlas Connection Test
Checks if your .env configuration is working
"""
import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

async def test_connection():
    """Test MongoDB Atlas connection with current .env settings"""
    
    print("🔗 MongoDB Atlas Connection Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME", "omnipricex_auth")
    
    print(f"📁 Database Name: {database_name}")
    
    # Check if URL is configured
    if not mongodb_url or "your-username:your-password" in mongodb_url:
        print("❌ MongoDB URL not configured!")
        print("\n🔧 To fix this:")
        print("1. Open .env file in this directory")
        print("2. Replace MONGODB_URL with your actual Atlas connection string")
        print("3. Format: mongodb+srv://username:password@cluster.xxxxx.mongodb.net/database?retryWrites=true&w=majority")
        return False
    
    # Hide password in output
    safe_url = mongodb_url.split('@')[1] if '@' in mongodb_url else mongodb_url
    print(f"🌐 Connecting to: {safe_url}")
    
    try:
        # Create client
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        
        # Test ping
        print("📡 Testing connection...")
        await client.admin.command('ping')
        print("✅ Ping successful!")
        
        # Test database access
        database = client[database_name]
        
        # Test basic operations
        print("🧪 Testing database operations...")
        
        # List collections (will be empty for new database)
        collections = await database.list_collection_names()
        print(f"📂 Collections found: {len(collections)}")
        if collections:
            print(f"   📄 {', '.join(collections)}")
        else:
            print("   📄 No collections yet (database is new)")
        
        # Test write/read
        test_collection = database.connection_test
        test_doc = {"test": True, "timestamp": "2025-08-03", "service": "auth"}
        
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Write test passed! Doc ID: {result.inserted_id}")
        
        # Read back
        doc = await test_collection.find_one({"_id": result.inserted_id})
        if doc:
            print("✅ Read test passed!")
        
        # Clean up
        await test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        # Close connection
        client.close()
        
        print("\n🎉 MongoDB Atlas connection successful!")
        print("Your auth service is ready to use this database.")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"Error: {str(e)}")
        
        # Common error solutions
        if "authentication failed" in str(e).lower():
            print("\n💡 Authentication Issue:")
            print("- Check username/password in connection string")
            print("- Verify database user exists in Atlas")
        elif "timeout" in str(e).lower() or "connection" in str(e).lower():
            print("\n💡 Network Issue:")
            print("- Check IP whitelist in Atlas Network Access")
            print("- Try adding 0.0.0.0/0 for development")
        elif "dns" in str(e).lower():
            print("\n💡 DNS Issue:")
            print("- Check cluster name in connection string")
            print("- Verify cluster is running")
        
        return False

def show_current_config():
    """Show current configuration from .env"""
    
    load_dotenv()
    
    print("\n📋 Current Configuration:")
    print("=" * 30)
    
    mongodb_url = os.getenv("MONGODB_URL", "Not set")
    database_name = os.getenv("DATABASE_NAME", "Not set")
    
    # Hide sensitive info
    if mongodb_url and mongodb_url != "Not set":
        if "your-username" in mongodb_url:
            print("📡 MongoDB URL: ⚠️ Template not replaced")
        else:
            # Show only the cluster part
            if '@' in mongodb_url:
                cluster_part = mongodb_url.split('@')[1].split('/')[0]
                print(f"📡 MongoDB Cluster: {cluster_part}")
            else:
                print("📡 MongoDB URL: ⚠️ Invalid format")
    else:
        print("📡 MongoDB URL: ❌ Not configured")
    
    print(f"📁 Database Name: {database_name}")
    
    # Check .env file exists
    if os.path.exists('.env'):
        print("📄 .env file: ✅ Found")
    else:
        print("📄 .env file: ❌ Missing")

if __name__ == "__main__":
    show_current_config()
    print("\nRunning connection test...")
    asyncio.run(test_connection())
