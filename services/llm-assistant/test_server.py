#!/usr/bin/env python3
"""
Simple gRPC server for LLM Assistant Service
"""

import asyncio
import grpc
import logging
import sys
from concurrent import futures

# Add project root to path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import llm_assistant_service_pb2_grpc
from app.service import LLMAssistantService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def serve():
    """Start the gRPC server"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the LLM service
    llm_assistant_service_pb2_grpc.add_LLMAssistantServiceServicer_to_server(
        LLMAssistantService(), server
    )
    
    # Listen on localhost:8002
    listen_addr = '[::]:8002'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"🚀 Starting LLM Assistant Service on {listen_addr}")
    
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down server...")
        await server.stop(5)

if __name__ == '__main__':
    asyncio.run(serve())
