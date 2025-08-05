#!/usr/bin/env python3
"""
Test client for Product Service
"""

import asyncio
import grpc
import sys
import os
from datetime import datetime

# Add proto directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(current_dir, '..', '..', 'shared', 'proto')
proto_dir = os.path.abspath(proto_dir)
sys.path.insert(0, proto_dir)

import product_service_pb2
import product_service_pb2_grpc


async def test_product_service():
    """Test the Product Service"""
    
    # Connect to the service
    channel = grpc.aio.insecure_channel('localhost:50053')
    stub = product_service_pb2_grpc.ProductServiceStub(channel)
    
    try:
        print("🧪 Testing Product Service...")
        
        # Test 1: Create a product
        print("\n1️⃣ Creating a test product...")
        create_request = product_service_pb2.CreateProductRequest(
            name="Test Product",
            sku="TEST-001",
            description="This is a test product",
            category="Electronics",
            brand="TestBrand",
            base_price=99.99,
            current_price=89.99,
            min_price=50.0,
            max_price=150.0,
            cost_price=40.0,
            stock_quantity=100,
            low_stock_threshold=10,
            competitor_urls={"competitor1": "https://example.com/product1"},
            tags=["test", "electronics"],
            created_by="test_user"
        )
        
        response = await stub.CreateProduct(create_request)
        if response.success:
            print(f"✅ Product created: {response.product.name} (ID: {response.product.id})")
            product_id = response.product.id
        else:
            print(f"❌ Failed to create product: {response.message}")
            return
        
        # Test 2: Get the product
        print("\n2️⃣ Retrieving the product...")
        get_request = product_service_pb2.GetProductRequest(id=product_id)
        response = await stub.GetProduct(get_request)
        if response.success:
            print(f"✅ Product retrieved: {response.product.name}")
            print(f"   - SKU: {response.product.sku}")
            print(f"   - Price: ${response.product.current_price}")
            print(f"   - Stock: {response.product.stock_quantity}")
        else:
            print(f"❌ Failed to get product: {response.message}")
        
        # Test 3: Update the product
        print("\n3️⃣ Updating the product...")
        update_request = product_service_pb2.UpdateProductRequest(
            id=product_id,
            name="Updated Test Product",
            current_price=79.99,
            stock_quantity=50
        )
        
        response = await stub.UpdateProduct(update_request)
        if response.success:
            print(f"✅ Product updated: {response.product.name}")
            print(f"   - New price: ${response.product.current_price}")
            print(f"   - New stock: {response.product.stock_quantity}")
        else:
            print(f"❌ Failed to update product: {response.message}")
        
        # Test 4: Update product price with history
        print("\n4️⃣ Updating product price...")
        price_request = product_service_pb2.UpdateProductPriceRequest(
            product_id=product_id,
            new_price=69.99,
            reason="Promotional discount",
            updated_by="test_user"
        )
        
        response = await stub.UpdateProductPrice(price_request)
        if response.success:
            print(f"✅ Price updated: ${response.product.current_price}")
        else:
            print(f"❌ Failed to update price: {response.message}")
        
        # Test 5: List products
        print("\n5️⃣ Listing products...")
        list_request = product_service_pb2.ListProductsRequest(
            page=1,
            limit=10,
            category="Electronics"
        )
        
        response = await stub.ListProducts(list_request)
        print(f"✅ Found {response.total} products:")
        for product in response.products:
            print(f"   - {product.name} (SKU: {product.sku}) - ${product.current_price}")
        
        # Test 6: Get products by category
        print("\n6️⃣ Getting products by category...")
        category_request = product_service_pb2.GetProductsByCategoryRequest(
            category="Electronics",
            page=1,
            limit=5
        )
        
        response = await stub.GetProductsByCategory(category_request)
        print(f"✅ Found {response.total} Electronics products")
        
        # Test 7: Create another product for low stock test
        print("\n7️⃣ Creating low stock product...")
        low_stock_request = product_service_pb2.CreateProductRequest(
            name="Low Stock Product",
            sku="LOW-001",
            description="Product with low stock",
            category="Electronics",
            brand="TestBrand",
            base_price=29.99,
            current_price=29.99,
            stock_quantity=5,  # Below default threshold of 10
            low_stock_threshold=10,
            created_by="test_user"
        )
        
        response = await stub.CreateProduct(low_stock_request)
        if response.success:
            print(f"✅ Low stock product created: {response.product.name}")
            low_stock_id = response.product.id
        
        # Test 8: Get low stock products
        print("\n8️⃣ Getting low stock products...")
        from google.protobuf.empty_pb2 import Empty
        response = await stub.GetLowStockProducts(Empty())
        print(f"✅ Found {response.total} low stock products:")
        for product in response.products:
            print(f"   - {product.name}: {product.stock_quantity} units (threshold: {product.low_stock_threshold})")
        
        # Test 9: Bulk update
        print("\n9️⃣ Bulk updating products...")
        bulk_request = product_service_pb2.BulkUpdateProductsRequest(
            updates=[
                product_service_pb2.UpdateProductRequest(
                    id=product_id,
                    current_price=59.99
                ),
                product_service_pb2.UpdateProductRequest(
                    id=low_stock_id,
                    stock_quantity=25
                )
            ],
            updated_by="test_user"
        )
        
        response = await stub.BulkUpdateProducts(bulk_request)
        print(f"✅ Bulk update completed: {response.total_updated} updated, {response.total_failed} failed")
        
        # Test 10: Delete products
        print("\n🔟 Deleting test products...")
        from google.protobuf.empty_pb2 import Empty
        
        delete_request1 = product_service_pb2.DeleteProductRequest(id=product_id)
        await stub.DeleteProduct(delete_request1)
        print(f"✅ Deleted product: {product_id}")
        
        delete_request2 = product_service_pb2.DeleteProductRequest(id=low_stock_id)
        await stub.DeleteProduct(delete_request2)
        print(f"✅ Deleted product: {low_stock_id}")
        
        print("\n🎉 All tests completed successfully!")
        
    except grpc.aio.AioRpcError as e:
        print(f"❌ gRPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await channel.close()


def main():
    """Main entry point"""
    print("🚀 Product Service Test Client")
    print("=" * 50)
    
    try:
        asyncio.run(test_product_service())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    main()
