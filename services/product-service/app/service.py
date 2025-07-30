import grpc
from app.proto import product_service_pb2
from app.proto import product_service_pb2_grpc
from app.database import Product, Price
from beanie.exceptions import DocumentNotFound

class ProductService(product_service_pb2_grpc.ProductServiceServicer):
    async def CreateProduct(self, request, context):
        try:
            product = Product(
                name=request.name,
                description=request.description,
                sku=request.sku,
                barcode=request.barcode,
                brand=request.brand,
                category=request.category,
                current_price=Price(value=request.price, currency=request.currency)
            )
            await product.insert()
            return product_service_pb2.ProductResponse(success=True, message="Product created successfully", product=product.dict())
        except Exception as e:
            return product_service_pb2.ProductResponse(success=False, message=str(e))

    async def GetProduct(self, request, context):
        try:
            product = await Product.get(request.id)
            if not product:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Product not found")
                return product_service_pb2.ProductResponse()
            return product_service_pb2.ProductResponse(success=True, product=product.dict())
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return product_service_pb2.ProductResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return product_service_pb2.ProductResponse()

    async def UpdateProduct(self, request, context):
        try:
            product = await Product.get(request.id)
            if not product:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Product not found")
                return product_service_pb2.ProductResponse()

            update_data = {
                "name": request.name,
                "description": request.description,
                "sku": request.sku,
                "barcode": request.barcode,
                "brand": request.brand,
                "category": request.category,
            }
            await product.update({"$set": update_data})
            return product_service_pb2.ProductResponse(success=True, message="Product updated successfully", product=product.dict())
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return product_service_pb2.ProductResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return product_service_pb2.ProductResponse()

    async def DeleteProduct(self, request, context):
        try:
            product = await Product.get(request.id)
            if not product:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Product not found")
                return product_service_pb2.DeleteProductResponse()
            await product.delete()
            return product_service_pb2.DeleteProductResponse(success=True, message="Product deleted successfully")
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return product_service_pb2.DeleteProductResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return product_service_pb2.DeleteProductResponse()

    async def ListProducts(self, request, context):
        try:
            products = await Product.find_all().to_list()
            return product_service_pb2.ListProductsResponse(products=[p.dict() for p in products])
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return product_service_pb2.ListProductsResponse()
