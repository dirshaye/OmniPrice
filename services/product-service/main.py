from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.database import User, Product, Price, ProductCompetitor
from app.service import ProductService
from app.proto import product_service_pb2_grpc

import grpc
from concurrent import futures

def create_app():
    app = FastAPI(
        title="Product Service",
        description="Product management microservice handling product catalog, pricing data, and competitor information within the OmniPriceX ecosystem.",
        version="0.1.0",
    )

    @app.on_event("startup")
    async def startup_event():
        client = AsyncIOMotorClient(settings.MONGO_URI)
        await init_beanie(
            database=client[settings.MONGO_DB],
            document_models=[User, Product, Price, ProductCompetitor],
        )

    return app

app = create_app()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
