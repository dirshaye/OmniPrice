#!/usr/bin/env python3
"""
Simple status check for Pricing Service
"""

import grpc
import sys
import os
import asyncio

# Add project root to path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import pricing_service_pb2
from shared.proto import pricing_service_pb2_grpc

async def check_service_status():
    """Check if the Pricing Service is running and responsive"""
    try:
        print("🔍 Checking Pricing Service status...")
        
        # Connect to the service
        channel = grpc.aio.insecure_channel('localhost:50052')
        stub = pricing_service_pb2_grpc.PricingServiceStub(channel)
        
        # Try to list pricing rules (should work even if empty)
        request = pricing_service_pb2.ListPricingRulesRequest(page=1, limit=1)
        response = await stub.ListPricingRules(request)
        
        print(f"✅ Pricing Service is running!")
        print(f"📊 Database contains {response.total} pricing rules")
        print(f"🔗 Service accessible at localhost:50052")
        
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
    print("🚀 Pricing Service Status Check")
    print("=" * 40)
    
    try:
        result = asyncio.run(check_service_status())
        if result:
            print("\n🎉 Pricing Service is healthy and ready!")
            sys.exit(0)
        else:
            print("\n💔 Pricing Service is not responding")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Status check interrupted")
        sys.exit(1)

if __name__ == "__main__":
    main()
