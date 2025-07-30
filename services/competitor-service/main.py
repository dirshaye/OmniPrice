from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.database import Competitor, CompetitorProduct
from app.service import CompetitorService
from app.proto import competitor_service_pb2_grpc

import grpc
from concurrent import futures

def create_app():
    app = FastAPI(
        title="Competitor Service",
        description="Manages competitors and their products.",
        version="0.1.0",
    )

    @app.on_event("startup")
    async def startup_event():
        client = AsyncIOMotorClient(settings.MONGO_URI)
        await init_beanie(
            database=client[settings.MONGO_DB],
            document_models=[Competitor, CompetitorProduct],
        )

    return app

app = create_app()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    competitor_service_pb2_grpc.add_CompetitorServiceServicer_to_server(CompetitorService(), server)
    server.add_insecure_port("[::]:50054")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
