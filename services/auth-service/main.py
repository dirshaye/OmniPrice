from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.database import User
from app.service import AuthService
from app.proto import auth_service_pb2_grpc

import grpc
from concurrent import futures

def create_app():
    app = FastAPI(
        title="Auth Service",
        description="Authentication and authorization microservice providing JWT-based security for the OmniPriceX platform.",
        version="0.1.0",
    )

    @app.on_event("startup")
    async def startup_event():
        client = AsyncIOMotorClient(settings.MONGO_URI)
        await init_beanie(
            database=client[settings.MONGO_DB],
            document_models=[User],
        )

    return app

app = create_app()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port("[::]:50056")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
