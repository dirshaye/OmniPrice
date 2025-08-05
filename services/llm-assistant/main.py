from fastapi import FastAPI
from app.service import LLMAssistantService
from app.proto import llm_assistant_service_pb2_grpc

import grpc
from concurrent import futures

def create_app():
    app = FastAPI(
        title="LLM Assistant Service",
        description="Provides LLM-powered insights and recommendations.",
        version="0.1.0",
    )
    return app

app = create_app()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    llm_assistant_service_pb2_grpc.add_LLMAssistantServiceServicer_to_server(LLMAssistantService(), server)
    server.add_insecure_port("[::]:50055")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
