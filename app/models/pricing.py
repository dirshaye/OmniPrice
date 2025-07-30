from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class PriceChangeReason(str, Enum):
    MANUAL = "manual"
    AUTO_RULE = "auto_rule"
    ML_MODEL = "ml_model"
    COMPETITOR_CHANGE = "competitor_change"
    INVENTORY_CHANGE = "inventory_change"
    SEASONAL = "seasonal"
    DEMAND_BASED = "demand_based"

class DecisionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"

class DecisionSource(str, Enum):
    MANUAL = "manual"
    RULE_ENGINE = "rule_engine"
    ML_MODEL = "ml_model"
    API = "api"
    GEMINI_AI = "gemini_ai"

class RuleType(str, Enum):
    UNDERCUT = "undercut"
    MARGIN_TARGET = "margin_target"
    STOCK_BASED = "stock_based"
    SEASONAL = "seasonal"
    DEMAND_BASED = "demand_based"
    CUSTOM = "custom"

# Price History Model
class PriceHistory(Document):
    """Track price changes over time"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Product reference
    product_id: str = Field(..., index=True)
    product_sku: Optional[str] = None
    
    # Competitor reference (if applicable)
    competitor_id: Optional[str] = None
    competitor_name: Optional[str] = None
    
    # Price data
    our_price: Optional[float] = Field(None, ge=0)
    competitor_price: Optional[float] = Field(None, ge=0)
    price_difference: Optional[float] = None
    price_difference_percentage: Optional[float] = None
    
    # Context
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    reason: PriceChangeReason = PriceChangeReason.MANUAL
    
    # Additional context
    market_conditions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    notes: Optional[str] = None
    
    class Settings:
        name = "price_history"
        indexes = [
            [("product_id", 1), ("timestamp", -1)],
            "timestamp",
            "competitor_id"
        ]

# Pricing Rule Model
class PricingRule(Document):
    """Define pricing rules and strategies"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Basic information
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    rule_type: RuleType
    
    # Target criteria
    product_ids: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Rule parameters
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Conditions
    conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Control
    is_active: bool = True
    priority: int = Field(default=0, ge=0)
    
    # Scheduling
    schedule_enabled: bool = False
    schedule_cron: Optional[str] = None
    timezone: str = "UTC"
    
    # Execution tracking
    last_executed: Optional[datetime] = None
    execution_count: int = Field(default=0, ge=0)
    success_count: int = Field(default=0, ge=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # User ID
    
    class Settings:
        name = "pricing_rules"
        indexes = [
            "rule_type",
            "is_active",
            "priority",
            "created_at"
        ]
    
    def __str__(self):
        return f"{self.name} ({self.rule_type})"

# Pricing Decision Model
class PricingDecision(Document):
    """Log all pricing decisions made by the system"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Product reference
    product_id: str = Field(..., index=True)
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    
    # Decision details
    old_price: float = Field(..., ge=0)
    new_price: float = Field(..., ge=0)
    price_change: float = Field(default=0)
    price_change_percentage: float = Field(default=0)
    
    # Source and context
    decision_source: DecisionSource
    applied_rule_id: Optional[str] = None
    applied_rule_name: Optional[str] = None
    
    # Confidence and reasoning
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    reasoning: Optional[str] = None
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Status
    status: DecisionStatus = DecisionStatus.PENDING
    
    # Approval workflow
    approved_by: Optional[str] = None  # User ID
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Execution
    applied_at: Optional[datetime] = None
    reverted_at: Optional[datetime] = None
    
    # Impact tracking
    estimated_impact: Optional[Dict[str, Any]] = Field(default_factory=dict)
    actual_impact: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    class Settings:
        name = "pricing_decisions"
        indexes = [
            [("product_id", 1), ("timestamp", -1)],
            "status",
            "decision_source",
            "timestamp"
        ]
    
    def __str__(self):
        return f"{self.product_name}: ${self.old_price} → ${self.new_price}"

# Pydantic schemas for API
class PricingRuleCreate(BaseModel):
    """Schema for creating pricing rules"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    rule_type: RuleType
    product_ids: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0)
    schedule_enabled: bool = False
    schedule_cron: Optional[str] = None
    timezone: str = "UTC"

class PricingRuleUpdate(BaseModel):
    """Schema for updating pricing rules"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    product_ids: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)
    schedule_enabled: Optional[bool] = None
    schedule_cron: Optional[str] = None
    timezone: Optional[str] = None

class PricingDecisionCreate(BaseModel):
    """Schema for creating pricing decisions"""
    product_id: str
    old_price: float = Field(..., ge=0)
    new_price: float = Field(..., ge=0)
    decision_source: DecisionSource
    applied_rule_id: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    reasoning: Optional[str] = None
    supporting_data: Dict[str, Any] = Field(default_factory=dict)

class PriceRecommendation(BaseModel):
    """Schema for price recommendations"""
    product_id: str
    current_price: float
    recommended_price: float
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    applied_rules: List[str] = Field(default_factory=list)
    competitor_analysis: Optional[Dict[str, Any]] = None
    estimated_impact: Optional[Dict[str, Any]] = None

class BulkPriceUpdate(BaseModel):
    """Schema for bulk price updates"""
    product_ids: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    rule_ids: Optional[List[str]] = None
    auto_apply: bool = False
    confidence_threshold: float = Field(default=0.7, ge=0, le=1)
