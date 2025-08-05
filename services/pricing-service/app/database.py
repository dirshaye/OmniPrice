"""
Pricing Service Database Models
"""

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RuleType(str, Enum):
    COMPETITOR_BASED = "competitor_based"
    MARGIN_BASED = "margin_based" 
    DEMAND_BASED = "demand_based"
    COST_PLUS = "cost_plus"
    DYNAMIC = "dynamic"
    PROMOTIONAL = "promotional"

class DecisionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    EXPIRED = "expired"

class DecisionSource(str, Enum):
    RULE_ENGINE = "rule_engine"
    LLM_ASSISTANT = "llm_assistant"
    MANUAL = "manual"
    SCHEDULED = "scheduled"

class PricingRule(Document):
    """Pricing rule definition"""
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    rule_type: RuleType = Field(..., description="Type of pricing rule")
    product_ids: List[str] = Field(default_factory=list, description="Specific product IDs")
    categories: List[str] = Field(default_factory=list, description="Product categories")
    brands: List[str] = Field(default_factory=list, description="Product brands")
    tags: List[str] = Field(default_factory=list, description="Product tags")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Rule parameters")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Rule conditions")
    is_active: bool = Field(default=True, description="Whether rule is active")
    priority: int = Field(default=1, description="Rule priority (higher = more important)")
    schedule_enabled: bool = Field(default=False, description="Whether rule is scheduled")
    schedule_cron: Optional[str] = Field(None, description="Cron expression for scheduling")
    timezone: str = Field(default="UTC", description="Timezone for scheduling")
    last_executed: Optional[datetime] = Field(None, description="Last execution time")
    execution_count: int = Field(default=0, description="Number of executions")
    success_count: int = Field(default=0, description="Number of successful executions")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="User who created the rule")

    class Settings:
        name = "pricing_rules"
        indexes = [
            "rule_type",
            "is_active",
            "priority",
            "created_at",
            [("rule_type", 1), ("is_active", 1), ("priority", -1)]
        ]

class PricingDecision(Document):
    """Pricing decision record"""
    product_id: str = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_sku: str = Field(..., description="Product SKU")
    old_price: float = Field(..., description="Current price")
    new_price: float = Field(..., description="Recommended new price")
    price_change: float = Field(..., description="Price change amount")
    price_change_percentage: float = Field(..., description="Price change percentage")
    decision_source: DecisionSource = Field(..., description="Source of decision")
    applied_rule_id: Optional[str] = Field(None, description="Applied rule ID")
    applied_rule_name: Optional[str] = Field(None, description="Applied rule name")
    confidence_score: float = Field(..., description="Confidence in decision")
    reasoning: str = Field(..., description="Reasoning for decision")
    supporting_data: Dict[str, Any] = Field(default_factory=dict, description="Supporting data")
    status: DecisionStatus = Field(default=DecisionStatus.PENDING, description="Decision status")
    approved_by: Optional[str] = Field(None, description="User who approved decision")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason")
    applied_at: Optional[datetime] = Field(None, description="Application timestamp")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "pricing_decisions"
        indexes = [
            "product_id",
            "status",
            "decision_source",
            "timestamp",
            [("product_id", 1), ("timestamp", -1)],
            [("status", 1), ("timestamp", -1)]
        ]

class PriceHistory(Document):
    """Price history tracking"""
    product_id: str = Field(..., description="Product ID")
    product_sku: str = Field(..., description="Product SKU")
    competitor_id: Optional[str] = Field(None, description="Competitor ID")
    competitor_name: Optional[str] = Field(None, description="Competitor name")
    our_price: float = Field(..., description="Our price")
    competitor_price: Optional[float] = Field(None, description="Competitor price")
    price_difference: Optional[float] = Field(None, description="Price difference")
    price_difference_percentage: Optional[float] = Field(None, description="Price difference %")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: str = Field(..., description="Reason for price change")
    market_conditions: Dict[str, Any] = Field(default_factory=dict, description="Market conditions")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Settings:
        name = "price_history"
        indexes = [
            "product_id",
            "timestamp",
            "competitor_id",
            [("product_id", 1), ("timestamp", -1)],
            [("competitor_id", 1), ("timestamp", -1)]
        ]

class PriceRecommendationModel(BaseModel):
    """Price recommendation model (not stored in DB)"""
    product_id: str
    current_price: float
    recommended_price: float
    confidence: float
    reasoning: str
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    applied_rules: List[str] = Field(default_factory=list)
    competitor_analysis: Dict[str, Any] = Field(default_factory=dict)
    estimated_impact: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)