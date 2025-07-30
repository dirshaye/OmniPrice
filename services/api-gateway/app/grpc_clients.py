import grpc
from app.proto import product_service_pb2
from app.proto import product_service_pb2_grpc

class GrpcClients:
    def __init__(self):
        self.product_channel = grpc.aio.insecure_channel("product-service:50051")
        self.product_stub = product_service_pb2_grpc.ProductServiceStub(self.product_channel)

    async def close(self):
        await self.product_channel.close()
