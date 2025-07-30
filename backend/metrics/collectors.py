from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import time
import logging

logger = logging.getLogger(__name__)

# Create a custom registry for OmniPriceX metrics
registry = CollectorRegistry()

# Scraping Metrics
scrapes_total = Counter(
    'omnipricex_scrapes_total',
    'Total number of scraping attempts',
    ['competitor', 'status'],
    registry=registry
)

scrape_duration_seconds = Histogram(
    'omnipricex_scrape_duration_seconds',
    'Time spent scraping competitor data',
    ['competitor'],
    registry=registry
)

scrape_errors_total = Counter(
    'omnipricex_scrape_errors_total',
    'Total number of scraping errors',
    ['competitor', 'error_type'],
    registry=registry
)

# Pricing Metrics
pricing_decisions_total = Counter(
    'omnipricex_pricing_decisions_total',
    'Total number of pricing decisions made',
    ['decision_source', 'status'],
    registry=registry
)

price_changes_total = Counter(
    'omnipricex_price_changes_total',
    'Total number of price changes applied',
    ['product_category', 'change_direction'],
    registry=registry
)

pricing_engine_duration_seconds = Histogram(
    'omnipricex_pricing_engine_duration_seconds',
    'Time spent generating price recommendations',
    ['rule_type'],
    registry=registry
)

recommendation_confidence = Histogram(
    'omnipricex_recommendation_confidence',
    'Confidence score of price recommendations',
    ['rule_type'],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=registry
)

# Task Queue Metrics
task_queue_latency_seconds = Histogram(
    'omnipricex_task_queue_latency_seconds',
    'Time tasks spend in queue before execution',
    ['task_type'],
    registry=registry
)

active_tasks_gauge = Gauge(
    'omnipricex_active_tasks',
    'Number of currently active tasks',
    ['task_type'],
    registry=registry
)

failed_tasks_total = Counter(
    'omnipricex_failed_tasks_total',
    'Total number of failed tasks',
    ['task_type', 'error_type'],
    registry=registry
)

# Business Metrics
products_monitored_gauge = Gauge(
    'omnipricex_products_monitored',
    'Number of products currently being monitored',
    registry=registry
)

competitors_tracked_gauge = Gauge(
    'omnipricex_competitors_tracked',
    'Number of competitors currently being tracked',
    registry=registry
)

average_price_change_percentage = Gauge(
    'omnipricex_average_price_change_percentage',
    'Average price change percentage in the last 24h',
    ['product_category'],
    registry=registry
)

# API Metrics
api_requests_total = Counter(
    'omnipricex_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

api_request_duration_seconds = Histogram(
    'omnipricex_api_request_duration_seconds',
    'Time spent processing API requests',
    ['method', 'endpoint'],
    registry=registry
)

# Database Metrics
database_connections_active = Gauge(
    'omnipricex_database_connections_active',
    'Number of active database connections',
    registry=registry
)

database_query_duration_seconds = Histogram(
    'omnipricex_database_query_duration_seconds',
    'Time spent on database queries',
    ['query_type'],
    registry=registry
)

class MetricsCollector:
    """Helper class to collect and expose metrics"""
    
    @staticmethod
    def record_scrape_attempt(competitor_name: str, status: str, duration: float = None):
        """Record a scraping attempt"""
        scrapes_total.labels(competitor=competitor_name, status=status).inc()
        if duration is not None:
            scrape_duration_seconds.labels(competitor=competitor_name).observe(duration)
    
    @staticmethod
    def record_scrape_error(competitor_name: str, error_type: str):
        """Record a scraping error"""
        scrape_errors_total.labels(competitor=competitor_name, error_type=error_type).inc()
    
    @staticmethod
    def record_pricing_decision(decision_source: str, status: str):
        """Record a pricing decision"""
        pricing_decisions_total.labels(decision_source=decision_source, status=status).inc()
    
    @staticmethod
    def record_price_change(product_category: str, old_price: float, new_price: float):
        """Record a price change"""
        direction = 'increase' if new_price > old_price else 'decrease'
        price_changes_total.labels(product_category=product_category, change_direction=direction).inc()
    
    @staticmethod
    def record_pricing_engine_execution(rule_type: str, duration: float, confidence: float):
        """Record pricing engine execution metrics"""
        pricing_engine_duration_seconds.labels(rule_type=rule_type).observe(duration)
        recommendation_confidence.labels(rule_type=rule_type).observe(confidence)
    
    @staticmethod
    def record_task_metrics(task_type: str, queue_time: float = None, status: str = 'success', error_type: str = None):
        """Record task execution metrics"""
        if queue_time is not None:
            task_queue_latency_seconds.labels(task_type=task_type).observe(queue_time)
        
        if status == 'failed' and error_type:
            failed_tasks_total.labels(task_type=task_type, error_type=error_type).inc()
    
    @staticmethod
    def update_business_metrics(products_count: int, competitors_count: int):
        """Update business-related metrics"""
        products_monitored_gauge.set(products_count)
        competitors_tracked_gauge.set(competitors_count)
    
    @staticmethod
    def record_api_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics"""
        api_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        api_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def get_metrics():
        """Get all metrics in Prometheus format"""
        return generate_latest(registry)

# Context managers for timing operations
class ScrapeTimer:
    """Context manager for timing scrape operations"""
    
    def __init__(self, competitor_name: str):
        self.competitor_name = competitor_name
        self.start_time = None
        self.status = 'success'
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is not None:
            self.status = 'failed'
            error_type = exc_type.__name__ if exc_type else 'unknown'
            MetricsCollector.record_scrape_error(self.competitor_name, error_type)
        
        MetricsCollector.record_scrape_attempt(self.competitor_name, self.status, duration)

class PricingEngineTimer:
    """Context manager for timing pricing engine operations"""
    
    def __init__(self, rule_type: str):
        self.rule_type = rule_type
        self.start_time = None
        self.confidence = 0.0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def set_confidence(self, confidence: float):
        """Set the confidence score for the recommendation"""
        self.confidence = confidence
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        MetricsCollector.record_pricing_engine_execution(self.rule_type, duration, self.confidence)

class APITimer:
    """Context manager for timing API requests"""
    
    def __init__(self, method: str, endpoint: str):
        self.method = method
        self.endpoint = endpoint
        self.start_time = None
        self.status_code = 200
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def set_status_code(self, status_code: int):
        """Set the response status code"""
        self.status_code = status_code
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is not None:
            self.status_code = 500
        
        MetricsCollector.record_api_request(self.method, self.endpoint, self.status_code, duration)
