from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from beanie import Document
from enum import Enum

# Enums for LLM Assistant
class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini" 
    ANTHROPIC = "anthropic"

class QueryType(str, Enum):
    PRICING_ANALYSIS = "pricing_analysis"
    COMPETITIVE_INSIGHTS = "competitive_insights"
    MARKET_TRENDS = "market_trends"
    PRODUCT_RECOMMENDATIONS = "product_recommendations"
    PRICE_OPTIMIZATION = "price_optimization"
    GENERAL_CHAT = "general_chat"

class SentimentScore(str, Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

# Database Documents
class LLMQuery(Document):
    """Store LLM queries and responses for analytics and caching"""
    
    user_id: str
    company_id: Optional[str] = None
    query_type: QueryType
    query_text: str
    context_data: Optional[Dict[str, Any]] = {}
    
    # LLM Configuration
    provider: LLMProvider
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    
    # Response
    response_text: str
    response_metadata: Optional[Dict[str, Any]] = {}
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    
    # Analysis
    sentiment: Optional[SentimentScore] = None
    confidence_score: Optional[float] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[int] = None
    
    class Settings:
        name = "llm_queries"
        indexes = [
            "user_id",
            "company_id", 
            "query_type",
            "provider",
            "created_at"
        ]

class InsightCache(Document):
    """Cache for frequently requested insights"""
    
    cache_key: str = Field(unique=True)  # Hash of query + context
    query_type: QueryType
    context_hash: str
    
    # Cached Response
    response_text: str
    metadata: Optional[Dict[str, Any]] = {}
    
    # Cache Management
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0
    expires_at: datetime
    
    class Settings:
        name = "insight_cache"
        indexes = ["cache_key", "query_type", "expires_at"]

# API Request/Response Models
class LLMQueryRequest(BaseModel):
    """Request model for LLM queries"""
    
    query: str = Field(..., min_length=1, max_length=2000, description="The question or prompt")
    query_type: QueryType = Field(default=QueryType.GENERAL_CHAT, description="Type of query")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context data")
    
    # LLM Settings (optional overrides)
    provider: Optional[LLMProvider] = Field(default=None, description="LLM provider to use")
    model: Optional[str] = Field(default=None, description="Specific model to use")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Response creativity")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4000, description="Maximum response length")
    
    # Options
    use_cache: bool = Field(default=True, description="Whether to use cached responses")
    store_query: bool = Field(default=True, description="Whether to store this query for analytics")

class LLMQueryResponse(BaseModel):
    """Response model for LLM queries"""
    
    response: str = Field(..., description="The LLM's response")
    query_type: QueryType = Field(..., description="Type of query processed")
    
    # Metadata
    provider: LLMProvider = Field(..., description="LLM provider used")
    model: str = Field(..., description="Model used")
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
    cost_usd: Optional[float] = Field(default=None, description="Estimated cost")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    
    # Analysis
    sentiment: Optional[SentimentScore] = Field(default=None, description="Response sentiment")
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence in response")
    
    # Cache Info
    from_cache: bool = Field(default=False, description="Whether response came from cache")
    cache_key: Optional[str] = Field(default=None, description="Cache key if applicable")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PricingAnalysisRequest(BaseModel):
    """Specialized request for pricing analysis"""
    
    product_id: str = Field(..., description="Product to analyze")
    competitors: Optional[List[str]] = Field(default=[], description="Competitor product IDs")
    market_context: Optional[Dict[str, Any]] = Field(default={}, description="Market conditions")
    analysis_type: Literal["optimization", "competitive", "trends", "forecast"] = Field(..., description="Type of analysis")

class PricingAnalysisResponse(BaseModel):
    """Specialized response for pricing analysis"""
    
    product_id: str
    current_price: Optional[float] = None
    recommended_price: Optional[float] = None
    price_range: Optional[Dict[str, float]] = None  # {"min": 10.0, "max": 15.0}
    
    # Analysis Results
    insights: List[str] = Field(default=[], description="Key insights")
    recommendations: List[str] = Field(default=[], description="Actionable recommendations")
    risk_factors: List[str] = Field(default=[], description="Potential risks")
    confidence_level: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Supporting Data
    market_position: Optional[str] = None
    competitive_advantage: List[str] = Field(default=[])
    demand_forecast: Optional[Dict[str, Any]] = None
    
    # Metadata
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = Field(default=[])

class ChatRequest(BaseModel):
    """Request for general chat/conversation"""
    
    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: Optional[str] = Field(default=None, description="Continue existing conversation")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Conversation context")

class ChatResponse(BaseModel):
    """Response for general chat"""
    
    message: str
    conversation_id: str
    suggestions: Optional[List[str]] = Field(default=[], description="Follow-up suggestions")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = "healthy"
    service: str = "llm-assistant"
    version: str = "1.0.0"
    providers_available: List[str] = Field(default=[])
    uptime_seconds: Optional[int] = None
