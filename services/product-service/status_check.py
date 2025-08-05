#!/usr/bin/env python3
"""
Simple status check for Product Service
"""

import grpc
import sys
import os
import asyncio

# Add proto directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(current_dir, '..', '..', 'shared', 'proto')
proto_dir = os.path.abspath(proto_dir)
sys.path.insert(0, proto_dir)

import product_service_pb2
import product_service_pb2_grpc

async def check_service_status():
    """Check if the Product Service is running and responsive"""
    try:
        print("🔍 Checking Product Service status...")
        
        # Connect to the service
        channel = grpc.aio.insecure_channel('localhost:50053')
        stub = product_service_pb2_grpc.ProductServiceStub(channel)
        
        # Try to list products (should work even if empty)
        request = product_service_pb2.ListProductsRequest(page=1, limit=1)
        response = await stub.ListProducts(request)
        
        print(f"✅ Product Service is running!")
        print(f"📊 Database contains {response.total} products")
        print(f"🔗 Service accessible at localhost:50053")
        
        await channel.close()
        return True
        
    except grpc.aio.AioRpcError as e:
        print(f"❌ gRPC Error: {e.code()} - {e.details()}")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def main():
    """Main entry point"""
    print("🚀 Product Service Status Check")
    print("=" * 40)
    
    try:
        result = asyncio.run(check_service_status())
        if result:
            print("\n🎉 Product Service is healthy and ready!")
            sys.exit(0)
        else:
            print("\n💔 Product Service is not responding")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Status check interrupted")
        sys.exit(1)

if __name__ == "__main__":
    main()
