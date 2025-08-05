import grpc
from typing import Dict, Optional
import logging
from contextlib import asynccontextmanager

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GRPCClientManager:
    """Manages gRPC connections to all microservices"""
    
    def __init__(self):
        self.channels: Dict[str, grpc.aio.Channel] = {}
        self.stubs: Dict[str, object] = {}
    
    async def initialize(self):
        """Initialize all gRPC connections"""
        try:
            # Import gRPC stubs
            from shared.proto import product_pb2_grpc, pricing_pb2_grpc, auth_pb2_grpc, scheduler_pb2_grpc, llm_pb2_grpc
            
            # Service configurations
            services = {
                'product': {
                    'host': settings.PRODUCT_SERVICE_HOST,
                    'port': settings.PRODUCT_SERVICE_PORT,
                    'stub_class': product_pb2_grpc.ProductServiceStub
                },
                'pricing': {
                    'host': settings.PRICING_SERVICE_HOST,
                    'port': settings.PRICING_SERVICE_PORT,
                    'stub_class': pricing_pb2_grpc.PricingServiceStub
                },
                'auth': {
                    'host': settings.AUTH_SERVICE_HOST,
                    'port': settings.AUTH_SERVICE_PORT,
                    'stub_class': auth_pb2_grpc.AuthServiceStub
                },
                'scheduler': {
                    'host': settings.SCHEDULER_SERVICE_HOST,
                    'port': settings.SCHEDULER_SERVICE_PORT,
                    'stub_class': scheduler_pb2_grpc.SchedulerServiceStub
                },
                'llm': {
                    'host': settings.LLM_SERVICE_HOST,
                    'port': settings.LLM_SERVICE_PORT,
                    'stub_class': llm_pb2_grpc.LLMServiceStub
                }
            }
            
            # Create channels and stubs for each service
            for service_name, config in services.items():
                address = f"{config['host']}:{config['port']}"
                
                # Create insecure channel (for internal communication)
                channel = grpc.aio.insecure_channel(address)
                self.channels[service_name] = channel
                
                # Create service stub
                stub = config['stub_class'](channel)
                self.stubs[service_name] = stub
                
                logger.info(f"Initialized gRPC client for {service_name} at {address}")
            
            # Test connections
            await self._test_connections()
            
        except Exception as e:
            logger.error(f"Failed to initialize gRPC clients: {e}")
            await self.cleanup()
            raise
    
    async def _test_connections(self):
        """Test connectivity to all services"""
        for service_name, channel in self.channels.items():
            try:
                # Try to connect with a timeout
                await channel.channel_ready()
                logger.info(f"Successfully connected to {service_name} service")
            except Exception as e:
                logger.warning(f"Failed to connect to {service_name} service: {e}")
    
    async def cleanup(self):
        """Close all gRPC connections"""
        for service_name, channel in self.channels.items():
            try:
                await channel.close()
                logger.info(f"Closed gRPC connection to {service_name}")
            except Exception as e:
                logger.error(f"Error closing connection to {service_name}: {e}")
        
        self.channels.clear()
        self.stubs.clear()
    
    def get_stub(self, service_name: str) -> Optional[object]:
        """Get gRPC stub for a specific service"""
        return self.stubs.get(service_name)
    
    def get_channel(self, service_name: str) -> Optional[grpc.aio.Channel]:
        """Get gRPC channel for a specific service"""
        return self.channels.get(service_name)
    
    async def health_check(self, service_name: str) -> bool:
        """Check if a specific service is healthy"""
        channel = self.get_channel(service_name)
        if not channel:
            return False
        
        try:
            # Check channel state
            state = channel.get_state()
            if state == grpc.ChannelConnectivity.READY:
                return True
            
            # Try to connect
            await channel.channel_ready()
            return True
            
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {e}")
            return False


# Global gRPC client manager instance
grpc_client_manager = GRPCClientManager()


@asynccontextmanager
async def get_grpc_client_manager():
    """Context manager for gRPC client manager"""
    try:
        yield grpc_client_manager
    finally:
        pass  # Don't cleanup on each use, only on app shutdown
