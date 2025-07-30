from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.database import PricingRule
from app.service import PricingService
from app.proto import pricing_service_pb2_grpc

import grpc
from concurrent import futures

def create_app():
    app = FastAPI(
        title="Pricing Service",
        description="AI-powered pricing engine microservice managing dynamic pricing rules, strategies, and optimization algorithms.",
        version="0.1.0",
    )

    @app.on_event("startup")
    async def startup_event():
        client = AsyncIOMotorClient(settings.MONGO_URI)
        await init_beanie(
            database=client[settings.MONGO_DB],
            document_models=[PricingRule],
        )

    return app

app = create_app()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pricing_service_pb2_grpc.add_PricingServiceServicer_to_server(PricingService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
