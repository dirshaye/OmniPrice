#!/usr/bin/env python3
"""
Product Service gRPC implementation
"""

import grpc
from datetime import datetime
from typing import Optional, List, Dict, Any
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.empty_pb2 import Empty
import logging
import sys
import os

# Add proto directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(current_dir, '..', '..', '..', 'shared', 'proto')
proto_dir = os.path.abspath(proto_dir)
sys.path.insert(0, proto_dir)

# Import proto files directly
import product_service_pb2
import product_service_pb2_grpc

# Import local models
from app.models import Product, ProductStatus, PriceHistory, CompetitorData
from beanie.exceptions import DocumentNotFound
from beanie.operators import Or, And, RegexQuery
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


class ProductService(product_service_pb2_grpc.ProductServiceServicer):
    """Product Service gRPC implementation"""
    
    def _datetime_to_timestamp(self, dt: datetime) -> Timestamp:
        """Convert datetime to protobuf Timestamp"""
        timestamp = Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp
    
    def _product_to_proto(self, product: Product) -> product_service_pb2.Product:
        """Convert Product document to protobuf Product"""
        proto_product = product_service_pb2.Product(
            id=str(product.id),
            name=product.name,
            sku=product.sku,
            description=product.description or "",
            category=product.category,
            brand=product.brand or "",
            base_price=product.base_price,
            current_price=product.current_price,
            min_price=product.min_price or 0.0,
            max_price=product.max_price or 0.0,
            cost_price=product.cost_price or 0.0,
            stock_quantity=product.stock_quantity,
            low_stock_threshold=product.low_stock_threshold,
            status=product.status.value,
            is_active=product.is_active,
            competitor_urls=product.competitor_urls,
            tags=product.tags,
            created_at=self._datetime_to_timestamp(product.created_at),
            updated_at=self._datetime_to_timestamp(product.updated_at),
            created_by=product.created_by
        )
        return proto_product
    
    async def CreateProduct(self, request, context):
        """Create a new product"""
        try:
            # Check if SKU already exists
            existing_product = await Product.find_one(Product.sku == request.sku)
            if existing_product:
                return product_service_pb2.ProductResponse(
                    success=False,
                    message=f"Product with SKU '{request.sku}' already exists"
                )
            
            # Create new product
            product = Product(
                name=request.name,
                sku=request.sku,
                description=request.description or None,
                category=request.category,
                brand=request.brand or None,
                base_price=request.base_price,
                current_price=request.current_price,
                min_price=request.min_price if request.min_price > 0 else None,
                max_price=request.max_price if request.max_price > 0 else None,
                cost_price=request.cost_price if request.cost_price > 0 else None,
                stock_quantity=request.stock_quantity,
                low_stock_threshold=request.low_stock_threshold,
                competitor_urls=dict(request.competitor_urls),
                tags=list(request.tags),
                created_by=request.created_by,
                status=ProductStatus.ACTIVE,
                is_active=True
            )
            
            # Add initial price history
            product.add_price_history(
                new_price=request.current_price,
                changed_by=request.created_by,
                reason="Initial product creation"
            )
            
            await product.insert()
            
            logger.info(f"✅ Created product: {product.name} (SKU: {product.sku})")
            
            return product_service_pb2.ProductResponse(
                success=True,
                message="Product created successfully",
                product=self._product_to_proto(product)
            )
            
        except DuplicateKeyError:
            return product_service_pb2.ProductResponse(
                success=False,
                message=f"Product with SKU '{request.sku}' already exists"
            )
        except Exception as e:
            logger.error(f"❌ Error creating product: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to create product: {str(e)}")
            return product_service_pb2.ProductResponse(
                success=False,
                message=f"Failed to create product: {str(e)}"
            )
    
    async def GetProduct(self, request, context):
        """Get a product by ID"""
        try:
            product = await Product.get(request.id)
            if not product:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Product not found")
                return product_service_pb2.ProductResponse(
                    success=False,
                    message="Product not found"
                )
            
            return product_service_pb2.ProductResponse(
                success=True,
                message="Product retrieved successfully",
                product=self._product_to_proto(product)
            )
            
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return product_service_pb2.ProductResponse(
                success=False,
                message="Product not found"
            )
        except Exception as e:
            logger.error(f"❌ Error getting product {request.id}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get product: {str(e)}")
            return product_service_pb2.ProductResponse(
                success=False,
                message=f"Failed to get product: {str(e)}"
            )
    
    async def UpdateProduct(self, request, context):
        """Update an existing product"""
        try:
            product = await Product.get(request.id)
            if not product:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Product not found")
                return product_service_pb2.ProductResponse(
                    success=False,
                    message="Product not found"
                )
            
            # Update fields that are provided
            update_data = {}
            if request.HasField("name"):
                update_data["name"] = request.name
            if request.HasField("description"):
                update_data["description"] = request.description
            if request.HasField("category"):
                update_data["category"] = request.category
            if request.HasField("brand"):
                update_data["brand"] = request.brand
            if request.HasField("base_price"):
                update_data["base_price"] = request.base_price
            if request.HasField("current_price"):
                # Add price history if price changed
                if request.current_price != product.current_price:
                    product.add_price_history(
                        new_price=request.current_price,
                        changed_by="system",  # In real implementation, get from auth context
                        reason="Price update via API"
                    )
                update_data["current_price"] = request.current_price
            if request.HasField("min_price"):
                update_data["min_price"] = request.min_price if request.min_price > 0 else None
            if request.HasField("max_price"):
                update_data["max_price"] = request.max_price if request.max_price > 0 else None
            if request.HasField("cost_price"):
                update_data["cost_price"] = request.cost_price if request.cost_price > 0 else None
            if request.HasField("stock_quantity"):
                update_data["stock_quantity"] = request.stock_quantity
            if request.HasField("low_stock_threshold"):
                update_data["low_stock_threshold"] = request.low_stock_threshold
            if request.HasField("status"):
                update_data["status"] = ProductStatus(request.status)
            if request.HasField("is_active"):
                update_data["is_active"] = request.is_active
            
            if request.competitor_urls:
                update_data["competitor_urls"] = dict(request.competitor_urls)
            if request.tags:
                update_data["tags"] = list(request.tags)
            
            update_data["updated_at"] = datetime.utcnow()
            
            # Apply updates
            for key, value in update_data.items():
                setattr(product, key, value)
            
            await product.save()
            
            logger.info(f"✅ Updated product: {product.name} (SKU: {product.sku})")
            
            return product_service_pb2.ProductResponse(
                success=True,
                message="Product updated successfully",
                product=self._product_to_proto(product)
            )
            
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return product_service_pb2.ProductResponse(
                success=False,
                message="Product not found"
            )
        except Exception as e:
            logger.error(f"❌ Error updating product {request.id}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to update product: {str(e)}")
            return product_service_pb2.ProductResponse(
                success=False,
                message=f"Failed to update product: {str(e)}"
            )
    
    async def DeleteProduct(self, request, context):
        """Delete a product"""
        try:
            product = await Product.get(request.id)
            if not product:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Product not found")
                return Empty()
            
            await product.delete()
            
            logger.info(f"✅ Deleted product: {product.name} (SKU: {product.sku})")
            
            return Empty()
            
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return Empty()
        except Exception as e:
            logger.error(f"❌ Error deleting product {request.id}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to delete product: {str(e)}")
            return Empty()
    
    async def ListProducts(self, request, context):
        """List products with pagination and filtering"""
        try:
            # Build query conditions
            conditions = []
            
            if request.HasField("category"):
                conditions.append(Product.category == request.category)
            if request.HasField("brand"):
                conditions.append(Product.brand == request.brand)
            if request.HasField("is_active"):
                conditions.append(Product.is_active == request.is_active)
            if request.HasField("search"):
                # Text search on name and description
                search_regex = RegexQuery(request.search, "i")
                conditions.append(
                    Or(
                        Product.name.regex(search_regex),
                        Product.description.regex(search_regex)
                    )
                )
            
            # Build final query
            if conditions:
                query = Product.find(And(*conditions))
            else:
                query = Product.find_all()
            
            # Get total count
            total = await query.count()
            
            # Apply pagination
            page = max(1, request.page) if request.page > 0 else 1
            limit = min(100, max(1, request.limit)) if request.limit > 0 else 20
            skip = (page - 1) * limit
            
            # Execute query with pagination
            products = await query.skip(skip).limit(limit).to_list()
            
            # Convert to proto
            proto_products = [self._product_to_proto(product) for product in products]
            
            has_next = (skip + limit) < total
            
            return product_service_pb2.ListProductsResponse(
                products=proto_products,
                total=total,
                page=page,
                limit=limit,
                has_next=has_next
            )
            
        except Exception as e:
            logger.error(f"❌ Error listing products: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to list products: {str(e)}")
            return product_service_pb2.ListProductsResponse()
    
    async def GetProductsByCategory(self, request, context):
        """Get products by category"""
        try:
            # Build query
            query = Product.find(Product.category == request.category)
            
            # Get total count
            total = await query.count()
            
            # Apply pagination
            page = max(1, request.page) if request.page > 0 else 1
            limit = min(100, max(1, request.limit)) if request.limit > 0 else 20
            skip = (page - 1) * limit
            
            # Execute query
            products = await query.skip(skip).limit(limit).to_list()
            
            # Convert to proto
            proto_products = [self._product_to_proto(product) for product in products]
            
            has_next = (skip + limit) < total
            
            return product_service_pb2.ListProductsResponse(
                products=proto_products,
                total=total,
                page=page,
                limit=limit,
                has_next=has_next
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting products by category {request.category}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get products by category: {str(e)}")
            return product_service_pb2.ListProductsResponse()
    
    async def GetLowStockProducts(self, request, context):
        """Get products with low stock"""
        try:
            # Find products where stock_quantity <= low_stock_threshold
            products = await Product.aggregate([
                {
                    "$match": {
                        "$expr": {
                            "$lte": ["$stock_quantity", "$low_stock_threshold"]
                        },
                        "is_active": True
                    }
                }
            ]).to_list()
            
            # Convert to Product objects and then to proto
            proto_products = []
            for product_data in products:
                product = Product(**product_data)
                proto_products.append(self._product_to_proto(product))
            
            return product_service_pb2.ListProductsResponse(
                products=proto_products,
                total=len(proto_products),
                page=1,
                limit=len(proto_products),
                has_next=False
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting low stock products: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get low stock products: {str(e)}")
            return product_service_pb2.ListProductsResponse()
    
    async def UpdateProductPrice(self, request, context):
        """Update product price with history tracking"""
        try:
            product = await Product.get(request.product_id)
            if not product:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Product not found")
                return product_service_pb2.ProductResponse(
                    success=False,
                    message="Product not found"
                )
            
            # Add price history and update current price
            product.add_price_history(
                new_price=request.new_price,
                changed_by=request.updated_by,
                reason=request.reason
            )
            
            await product.save()
            
            logger.info(f"✅ Updated price for product {product.name}: {product.current_price}")
            
            return product_service_pb2.ProductResponse(
                success=True,
                message="Product price updated successfully",
                product=self._product_to_proto(product)
            )
            
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return product_service_pb2.ProductResponse(
                success=False,
                message="Product not found"
            )
        except Exception as e:
            logger.error(f"❌ Error updating product price {request.product_id}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to update product price: {str(e)}")
            return product_service_pb2.ProductResponse(
                success=False,
                message=f"Failed to update product price: {str(e)}"
            )
    
    async def BulkUpdateProducts(self, request, context):
        """Bulk update multiple products"""
        try:
            total_updated = 0
            total_failed = 0
            failed_ids = []
            error_messages = []
            
            for update_request in request.updates:
                try:
                    product = await Product.get(update_request.id)
                    if not product:
                        total_failed += 1
                        failed_ids.append(update_request.id)
                        error_messages.append(f"Product {update_request.id} not found")
                        continue
                    
                    # Apply updates (similar to UpdateProduct but simplified)
                    update_data = {}
                    if update_request.HasField("name"):
                        update_data["name"] = update_request.name
                    if update_request.HasField("description"):
                        update_data["description"] = update_request.description
                    if update_request.HasField("category"):
                        update_data["category"] = update_request.category
                    if update_request.HasField("brand"):
                        update_data["brand"] = update_request.brand
                    if update_request.HasField("current_price"):
                        if update_request.current_price != product.current_price:
                            product.add_price_history(
                                new_price=update_request.current_price,
                                changed_by=request.updated_by,
                                reason="Bulk update"
                            )
                        update_data["current_price"] = update_request.current_price
                    if update_request.HasField("stock_quantity"):
                        update_data["stock_quantity"] = update_request.stock_quantity
                    if update_request.HasField("is_active"):
                        update_data["is_active"] = update_request.is_active
                    
                    update_data["updated_at"] = datetime.utcnow()
                    
                    # Apply updates
                    for key, value in update_data.items():
                        setattr(product, key, value)
                    
                    await product.save()
                    total_updated += 1
                    
                except Exception as e:
                    total_failed += 1
                    failed_ids.append(update_request.id)
                    error_messages.append(f"Error updating {update_request.id}: {str(e)}")
                    logger.error(f"❌ Error in bulk update for product {update_request.id}: {e}")
            
            logger.info(f"✅ Bulk update completed: {total_updated} updated, {total_failed} failed")
            
            return product_service_pb2.BulkUpdateProductsResponse(
                total_updated=total_updated,
                total_failed=total_failed,
                failed_ids=failed_ids,
                error_messages=error_messages
            )
            
        except Exception as e:
            logger.error(f"❌ Error in bulk update: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to bulk update products: {str(e)}")
            return product_service_pb2.BulkUpdateProductsResponse(
                total_updated=0,
                total_failed=len(request.updates),
                failed_ids=[update.id for update in request.updates],
                error_messages=[f"Bulk update failed: {str(e)}"]
            )
