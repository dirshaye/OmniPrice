"""
Health checking utilities - Enterprise pattern for service health monitoring.
Used by Kubernetes, AWS ECS for service health checks.
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod


class HealthStatus(Enum):
    """Health check status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None


class HealthCheck(ABC):
    """Abstract base class for health checks"""
    
    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout
    
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform the health check"""
        pass


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity"""
    
    def __init__(self, db_client, name: str = "database", timeout: float = 5.0):
        super().__init__(name, timeout)
        self.db_client = db_client
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            # Try to ping the database
            await asyncio.wait_for(
                self.db_client.admin.command('ping'),
                timeout=self.timeout
            )
            
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection is healthy",
                duration_ms=duration_ms
            )
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Database connection timeout",
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                duration_ms=duration_ms
            )


class GRPCServiceHealthCheck(HealthCheck):
    """Health check for gRPC service connectivity"""
    
    def __init__(self, service_url: str, name: str, timeout: float = 5.0):
        super().__init__(name, timeout)
        self.service_url = service_url
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            import grpc
            
            # Create channel and check connectivity
            channel = grpc.aio.insecure_channel(self.service_url)
            await asyncio.wait_for(
                channel.channel_ready(),
                timeout=self.timeout
            )
            await channel.close()
            
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message=f"gRPC service {self.service_url} is healthy",
                duration_ms=duration_ms
            )
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"gRPC service {self.service_url} timeout",
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"gRPC service {self.service_url} failed: {str(e)}",
                duration_ms=duration_ms
            )


class CustomHealthCheck(HealthCheck):
    """Custom health check using a callable"""
    
    def __init__(self, name: str, check_func: Callable[[], Any], timeout: float = 5.0):
        super().__init__(name, timeout)
        self.check_func = check_func
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            if asyncio.iscoroutinefunction(self.check_func):
                result = await asyncio.wait_for(
                    self.check_func(),
                    timeout=self.timeout
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(self.check_func),
                    timeout=self.timeout
                )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if result:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message=f"{self.name} check passed",
                    duration_ms=duration_ms
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"{self.name} check failed",
                    duration_ms=duration_ms
                )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"{self.name} check error: {str(e)}",
                duration_ms=duration_ms
            )


class HealthChecker:
    """Centralized health checker for microservices"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.checks: List[HealthCheck] = []
        self.startup_time = time.time()
    
    def add_check(self, health_check: HealthCheck):
        """Add a health check"""
        self.checks.append(health_check)
    
    def add_database_check(self, db_client, name: str = "database"):
        """Add database health check"""
        self.add_check(DatabaseHealthCheck(db_client, name))
    
    def add_grpc_service_check(self, service_url: str, name: str):
        """Add gRPC service health check"""
        self.add_check(GRPCServiceHealthCheck(service_url, name))
    
    def add_custom_check(self, name: str, check_func: Callable):
        """Add custom health check"""
        self.add_check(CustomHealthCheck(name, check_func))
    
    async def check_health(self) -> Dict[str, Any]:
        """Perform all health checks"""
        results = []
        overall_status = HealthStatus.HEALTHY
        
        # Run all health checks concurrently
        if self.checks:
            check_results = await asyncio.gather(
                *[check.check() for check in self.checks],
                return_exceptions=True
            )
            
            for result in check_results:
                if isinstance(result, Exception):
                    results.append(HealthCheckResult(
                        name="unknown",
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check exception: {str(result)}"
                    ))
                    overall_status = HealthStatus.UNHEALTHY
                else:
                    results.append(result)
                    if result.status == HealthStatus.UNHEALTHY:
                        overall_status = HealthStatus.UNHEALTHY
                    elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED
        
        return {
            "service": self.service_name,
            "status": overall_status.value,
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.startup_time,
            "checks": [
                {
                    "name": result.name,
                    "status": result.status.value,
                    "message": result.message,
                    "duration_ms": result.duration_ms,
                    "details": result.details
                }
                for result in results
            ]
        }
    
    async def liveness_check(self) -> Dict[str, Any]:
        """Simple liveness check (just return that service is running)"""
        return {
            "service": self.service_name,
            "status": "alive",
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.startup_time
        }
    
    async def readiness_check(self) -> Dict[str, Any]:
        """Readiness check (check if service is ready to handle requests)"""
        health_result = await self.check_health()
        is_ready = health_result["status"] in ["healthy", "degraded"]
        
        return {
            "service": self.service_name,
            "status": "ready" if is_ready else "not_ready",
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.startup_time,
            "health": health_result
        }
