"""
Shared configuration module for OmniPriceX microservices.
"""

from .settings import (
    BaseServiceSettings,
    APIGatewaySettings,
    ProductServiceSettings,
    PricingServiceSettings,
    ScraperServiceSettings,
    CompetitorServiceSettings,
    AnalyticsServiceSettings,
    LLMAssistantServiceSettings,
    AuthServiceSettings,
)

__all__ = [
    "BaseServiceSettings",
    "APIGatewaySettings", 
    "ProductServiceSettings",
    "PricingServiceSettings",
    "ScraperServiceSettings",
    "CompetitorServiceSettings",
    "AnalyticsServiceSettings",
    "LLMAssistantServiceSettings",
    "AuthServiceSettings",
]
