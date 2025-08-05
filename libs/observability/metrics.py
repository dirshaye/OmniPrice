"""
Prometheus metrics collection - Industry standard for monitoring.
Used by Google, Netflix, Uber for service metrics.
"""

import time
from typing import Dict, Optional
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from prometheus_client.exposition import choose_encoder


class MetricsRegistry:
    """Central metrics registry for a microservice"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.registry = CollectorRegistry()
        
        # Standard service metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'service'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint', 'service'],
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'active_connections',
            'Active connections',
            ['service'],
            registry=self.registry
        )
        
        self.grpc_requests = Counter(
            'grpc_requests_total',
            'Total gRPC requests',
            ['method', 'service', 'status'],
            registry=self.registry
        )
        
        self.database_operations = Counter(
            'database_operations_total',
            'Database operations',
            ['operation', 'collection', 'service'],
            registry=self.registry
        )
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.request_count.labels(
            method=method,
            endpoint=endpoint, 
            status_code=status_code,
            service=self.service_name
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint,
            service=self.service_name
        ).observe(duration)
    
    def record_grpc_request(self, method: str, status: str):
        """Record gRPC request metrics"""
        self.grpc_requests.labels(
            method=method,
            service=self.service_name,
            status=status
        ).inc()
    
    def record_db_operation(self, operation: str, collection: str):
        """Record database operation metrics"""
        self.database_operations.labels(
            operation=operation,
            collection=collection,
            service=self.service_name
        ).inc()
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry).decode('utf-8')


# Global metrics registry
_metrics_registry: Optional[MetricsRegistry] = None


def setup_metrics(service_name: str) -> MetricsRegistry:
    """Setup metrics collection for a service"""
    global _metrics_registry
    _metrics_registry = MetricsRegistry(service_name)
    return _metrics_registry


def get_metrics_registry() -> Optional[MetricsRegistry]:
    """Get the global metrics registry"""
    return _metrics_registry


class MetricsMiddleware:
    """Middleware to automatically collect HTTP metrics"""
    
    def __init__(self, app, service_name: str):
        self.app = app
        self.service_name = service_name
        self.metrics = get_metrics_registry()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and self.metrics:
            start_time = time.time()
            
            # Capture response status
            status_code = 200
            
            async def send_wrapper(message):
                nonlocal status_code
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
            
            # Record metrics
            duration = time.time() - start_time
            self.metrics.record_request(
                method=scope["method"],
                endpoint=scope["path"],
                status_code=status_code,
                duration=duration
            )
        else:
            await self.app(scope, receive, send)
