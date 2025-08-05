"""
Pricing Engine - Core pricing logic and algorithms
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import math

from .database import (
    PricingRule, PricingDecision, PriceHistory, PriceRecommendationModel,
    RuleType, DecisionSource, DecisionStatus
)
from .config import settings

logger = logging.getLogger(__name__)

class PricingEngine:
    """Core pricing engine with various pricing strategies"""
    
    def __init__(self):
        self.confidence_threshold = settings.DEFAULT_CONFIDENCE_THRESHOLD
        self.max_price_change = settings.MAX_PRICE_CHANGE_PERCENTAGE
        self.min_price = settings.MIN_PRICE_THRESHOLD
    
    async def recommend_price(
        self, 
        product_id: str,
        current_price: float,
        rule_ids: List[str] = None,
        include_competitor_analysis: bool = True,
        include_impact_estimation: bool = True
    ) -> PriceRecommendationModel:
        """Generate price recommendation for a single product"""
        
        logger.info(f"🎯 Generating price recommendation for product {product_id}")
        
        try:
            # Get applicable rules
            rules = await self._get_applicable_rules(product_id, rule_ids)
            
            # Get product context (price history, competitors, etc.)
            context = await self._get_product_context(product_id)
            
            # Apply pricing rules
            recommendations = []
            applied_rules = []
            
            for rule in rules:
                try:
                    rec_price, confidence, reasoning = await self._apply_rule(
                        rule, product_id, current_price, context
                    )
                    
                    if rec_price is not None:
                        recommendations.append({
                            'price': rec_price,
                            'confidence': confidence,
                            'reasoning': reasoning,
                            'rule_id': str(rule.id),
                            'rule_name': rule.name,
                            'rule_type': rule.rule_type
                        })
                        applied_rules.append(f"{rule.name} ({rule.rule_type})")
                        
                except Exception as e:
                    logger.error(f"Error applying rule {rule.name}: {e}")
                    continue
            
            # Aggregate recommendations
            if not recommendations:
                # Fallback: return current price with low confidence
                final_price = current_price
                final_confidence = 0.1
                reasoning = "No applicable rules found. Maintaining current price."
            else:
                final_price, final_confidence, reasoning = self._aggregate_recommendations(
                    recommendations, current_price
                )
            
            # Validate price bounds
            final_price = self._validate_price_bounds(final_price, current_price)
            
            # Get competitor analysis if requested
            competitor_analysis = {}
            if include_competitor_analysis:
                competitor_analysis = await self._analyze_competitors(product_id, context)
            
            # Estimate impact if requested
            estimated_impact = {}
            if include_impact_estimation:
                estimated_impact = await self._estimate_impact(
                    product_id, current_price, final_price, context
                )
            
            return PriceRecommendationModel(
                product_id=product_id,
                current_price=current_price,
                recommended_price=final_price,
                confidence=final_confidence,
                reasoning=reasoning,
                supporting_data=context,
                applied_rules=applied_rules,
                competitor_analysis=competitor_analysis,
                estimated_impact=estimated_impact
            )
            
        except Exception as e:
            logger.error(f"Error generating price recommendation: {e}")
            # Return safe fallback
            return PriceRecommendationModel(
                product_id=product_id,
                current_price=current_price,
                recommended_price=current_price,
                confidence=0.0,
                reasoning=f"Error in pricing engine: {str(e)}",
                supporting_data={},
                applied_rules=[],
                competitor_analysis={},
                estimated_impact={}
            )
    
    async def bulk_recommend_prices(
        self,
        product_ids: List[str],
        categories: List[str] = None,
        brands: List[str] = None,
        rule_ids: List[str] = None,
        include_competitor_analysis: bool = False,
        confidence_threshold: float = None
    ) -> List[PriceRecommendationModel]:
        """Generate bulk price recommendations"""
        
        threshold = confidence_threshold or self.confidence_threshold
        logger.info(f"🎯 Generating bulk price recommendations for {len(product_ids)} products")
        
        recommendations = []
        
        # Process products in batches to avoid overwhelming the system
        batch_size = 10
        for i in range(0, len(product_ids), batch_size):
            batch = product_ids[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for product_id in batch:
                # For bulk operations, we'll use a simplified current price lookup
                current_price = await self._get_current_price(product_id)
                if current_price:
                    task = self.recommend_price(
                        product_id=product_id,
                        current_price=current_price,
                        rule_ids=rule_ids,
                        include_competitor_analysis=include_competitor_analysis,
                        include_impact_estimation=False  # Skip for bulk to improve performance
                    )
                    tasks.append(task)
            
            if tasks:
                batch_recommendations = await asyncio.gather(*tasks, return_exceptions=True)
                
                for rec in batch_recommendations:
                    if isinstance(rec, PriceRecommendationModel) and rec.confidence >= threshold:
                        recommendations.append(rec)
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations above confidence threshold")
        return recommendations
    
    async def _get_applicable_rules(self, product_id: str, rule_ids: List[str] = None) -> List[PricingRule]:
        """Get pricing rules applicable to a product"""
        
        query = {"is_active": True}
        
        if rule_ids:
            from beanie import PydanticObjectId
            object_ids = [PydanticObjectId(rid) for rid in rule_ids if PydanticObjectId.is_valid(rid)]
            query["_id"] = {"$in": object_ids}
        
        rules = await PricingRule.find(query).sort(-PricingRule.priority).to_list()
        
        # Filter rules that apply to this product
        applicable_rules = []
        for rule in rules:
            if await self._rule_applies_to_product(rule, product_id):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    async def _rule_applies_to_product(self, rule: PricingRule, product_id: str) -> bool:
        """Check if a rule applies to a specific product"""
        
        # If rule has specific product IDs, check if this product is included
        if rule.product_ids and product_id not in rule.product_ids:
            return False
        
        # TODO: Add logic to check categories, brands, tags against product data
        # This would require calling the Product Service to get product details
        
        return True
    
    async def _get_product_context(self, product_id: str) -> Dict[str, Any]:
        """Get contextual data for pricing decisions"""
        
        context = {
            "product_id": product_id,
            "price_history": [],
            "competitor_prices": [],
            "market_conditions": {},
            "demand_indicators": {}
        }
        
        try:
            # Get recent price history
            history = await PriceHistory.find(
                PriceHistory.product_id == product_id
            ).sort(-PriceHistory.timestamp).limit(30).to_list()
            
            context["price_history"] = [
                {
                    "timestamp": h.timestamp.isoformat(),
                    "our_price": h.our_price,
                    "competitor_price": h.competitor_price,
                    "reason": h.reason
                }
                for h in history
            ]
            
            # Aggregate competitor data
            competitor_prices = {}
            for h in history:
                if h.competitor_id and h.competitor_price:
                    if h.competitor_id not in competitor_prices:
                        competitor_prices[h.competitor_id] = []
                    competitor_prices[h.competitor_id].append({
                        "price": h.competitor_price,
                        "timestamp": h.timestamp.isoformat()
                    })
            
            context["competitor_prices"] = competitor_prices
            
        except Exception as e:
            logger.error(f"Error getting product context: {e}")
        
        return context
    
    async def _apply_rule(
        self, 
        rule: PricingRule, 
        product_id: str, 
        current_price: float, 
        context: Dict[str, Any]
    ) -> Tuple[Optional[float], float, str]:
        """Apply a specific pricing rule"""
        
        try:
            if rule.rule_type == RuleType.COMPETITOR_BASED:
                return await self._apply_competitor_rule(rule, current_price, context)
            elif rule.rule_type == RuleType.MARGIN_BASED:
                return await self._apply_margin_rule(rule, current_price, context)
            elif rule.rule_type == RuleType.DEMAND_BASED:
                return await self._apply_demand_rule(rule, current_price, context)
            elif rule.rule_type == RuleType.COST_PLUS:
                return await self._apply_cost_plus_rule(rule, current_price, context)
            elif rule.rule_type == RuleType.DYNAMIC:
                return await self._apply_dynamic_rule(rule, current_price, context)
            elif rule.rule_type == RuleType.PROMOTIONAL:
                return await self._apply_promotional_rule(rule, current_price, context)
            else:
                return None, 0.0, f"Unknown rule type: {rule.rule_type}"
                
        except Exception as e:
            logger.error(f"Error applying rule {rule.name}: {e}")
            return None, 0.0, f"Error applying rule: {str(e)}"
    
    async def _apply_competitor_rule(self, rule: PricingRule, current_price: float, context: Dict[str, Any]) -> Tuple[float, float, str]:
        """Apply competitor-based pricing rule"""
        
        competitor_prices = context.get("competitor_prices", {})
        if not competitor_prices:
            return current_price, 0.2, "No competitor data available"
        
        # Get recent competitor prices
        recent_prices = []
        for competitor_id, prices in competitor_prices.items():
            if prices:
                recent_prices.append(prices[0]["price"])  # Most recent price
        
        if not recent_prices:
            return current_price, 0.2, "No recent competitor prices"
        
        avg_competitor_price = sum(recent_prices) / len(recent_prices)
        min_competitor_price = min(recent_prices)
        max_competitor_price = max(recent_prices)
        
        # Get rule parameters
        params = rule.parameters
        strategy = params.get("strategy", "match_average")  # match_average, undercut, premium
        margin = params.get("margin", 0.0)  # Percentage margin
        
        if strategy == "match_average":
            recommended_price = avg_competitor_price * (1 + margin / 100)
            reasoning = f"Matching average competitor price (${avg_competitor_price:.2f}) with {margin}% margin"
        elif strategy == "undercut":
            undercut_amount = params.get("undercut_percentage", 5.0)
            recommended_price = min_competitor_price * (1 - undercut_amount / 100)
            reasoning = f"Undercutting minimum competitor price by {undercut_amount}%"
        elif strategy == "premium":
            premium_amount = params.get("premium_percentage", 10.0)
            recommended_price = max_competitor_price * (1 + premium_amount / 100)
            reasoning = f"Premium pricing at {premium_amount}% above maximum competitor"
        else:
            recommended_price = avg_competitor_price
            reasoning = "Default: matching average competitor price"
        
        confidence = min(0.8, len(recent_prices) * 0.2)  # Higher confidence with more data
        
        return recommended_price, confidence, reasoning
    
    async def _apply_margin_rule(self, rule: PricingRule, current_price: float, context: Dict[str, Any]) -> Tuple[float, float, str]:
        """Apply margin-based pricing rule"""
        
        params = rule.parameters
        target_margin = params.get("target_margin_percentage", 20.0)
        cost_price = params.get("cost_price", current_price * 0.7)  # Estimate if not provided
        
        recommended_price = cost_price * (1 + target_margin / 100)
        reasoning = f"Target margin of {target_margin}% on cost of ${cost_price:.2f}"
        confidence = 0.7  # High confidence for cost-based pricing
        
        return recommended_price, confidence, reasoning
    
    async def _apply_demand_rule(self, rule: PricingRule, current_price: float, context: Dict[str, Any]) -> Tuple[float, float, str]:
        """Apply demand-based pricing rule"""
        
        # This is a simplified implementation
        # In a real system, you'd integrate with demand forecasting models
        
        params = rule.parameters
        demand_elasticity = params.get("demand_elasticity", -1.5)
        base_demand = params.get("base_demand", 100)
        
        # Simulate demand-based pricing adjustment
        if demand_elasticity < -1:  # Elastic demand
            price_adjustment = -0.05  # Reduce price to increase demand
            reasoning = "Elastic demand detected: reducing price to increase volume"
        else:  # Inelastic demand
            price_adjustment = 0.05  # Increase price for higher margins
            reasoning = "Inelastic demand detected: increasing price for higher margins"
        
        recommended_price = current_price * (1 + price_adjustment)
        confidence = 0.5  # Medium confidence for demand-based models
        
        return recommended_price, confidence, reasoning
    
    async def _apply_cost_plus_rule(self, rule: PricingRule, current_price: float, context: Dict[str, Any]) -> Tuple[float, float, str]:
        """Apply cost-plus pricing rule"""
        
        params = rule.parameters
        markup_percentage = params.get("markup_percentage", 50.0)
        cost_price = params.get("cost_price", current_price * 0.6)  # Estimate if not provided
        
        recommended_price = cost_price * (1 + markup_percentage / 100)
        reasoning = f"Cost-plus pricing: {markup_percentage}% markup on cost of ${cost_price:.2f}"
        confidence = 0.8  # High confidence for straightforward cost-plus
        
        return recommended_price, confidence, reasoning
    
    async def _apply_dynamic_rule(self, rule: PricingRule, current_price: float, context: Dict[str, Any]) -> Tuple[float, float, str]:
        """Apply dynamic pricing rule combining multiple factors"""
        
        params = rule.parameters
        
        # Weight factors
        competitor_weight = params.get("competitor_weight", settings.COMPETITOR_PRICE_WEIGHT)
        demand_weight = params.get("demand_weight", settings.MARKET_DEMAND_WEIGHT)
        cost_weight = params.get("cost_weight", settings.COST_MARGIN_WEIGHT)
        
        # Get component recommendations
        competitor_price, _, _ = await self._apply_competitor_rule(rule, current_price, context)
        demand_price, _, _ = await self._apply_demand_rule(rule, current_price, context)
        cost_price, _, _ = await self._apply_cost_plus_rule(rule, current_price, context)
        
        # Weighted average
        total_weight = competitor_weight + demand_weight + cost_weight
        recommended_price = (
            competitor_price * competitor_weight +
            demand_price * demand_weight +
            cost_price * cost_weight
        ) / total_weight
        
        reasoning = f"Dynamic pricing combining competitor ({competitor_weight:.1f}), demand ({demand_weight:.1f}), and cost ({cost_weight:.1f}) factors"
        confidence = 0.9  # High confidence for multi-factor approach
        
        return recommended_price, confidence, reasoning
    
    async def _apply_promotional_rule(self, rule: PricingRule, current_price: float, context: Dict[str, Any]) -> Tuple[float, float, str]:
        """Apply promotional pricing rule"""
        
        params = rule.parameters
        discount_percentage = params.get("discount_percentage", 10.0)
        min_price = params.get("min_price", current_price * 0.5)
        
        recommended_price = max(current_price * (1 - discount_percentage / 100), min_price)
        reasoning = f"Promotional pricing: {discount_percentage}% discount (minimum ${min_price:.2f})"
        confidence = 0.6  # Medium confidence for promotional pricing
        
        return recommended_price, confidence, reasoning
    
    def _aggregate_recommendations(self, recommendations: List[Dict], current_price: float) -> Tuple[float, float, str]:
        """Aggregate multiple price recommendations"""
        
        if not recommendations:
            return current_price, 0.0, "No recommendations to aggregate"
        
        # Weight recommendations by confidence and rule priority
        total_weighted_price = 0
        total_weight = 0
        reasoning_parts = []
        
        for rec in recommendations:
            weight = rec["confidence"]
            total_weighted_price += rec["price"] * weight
            total_weight += weight
            reasoning_parts.append(f"{rec['rule_name']}: ${rec['price']:.2f} (conf: {rec['confidence']:.2f})")
        
        if total_weight == 0:
            return current_price, 0.0, "All recommendations had zero confidence"
        
        final_price = total_weighted_price / total_weight
        final_confidence = min(total_weight / len(recommendations), 1.0)
        
        reasoning = f"Aggregated from {len(recommendations)} rules: " + "; ".join(reasoning_parts)
        
        return final_price, final_confidence, reasoning
    
    def _validate_price_bounds(self, recommended_price: float, current_price: float) -> float:
        """Validate and adjust price within acceptable bounds"""
        
        # Minimum price check
        if recommended_price < self.min_price:
            return self.min_price
        
        # Maximum change percentage check
        price_change_pct = abs((recommended_price - current_price) / current_price) * 100
        if price_change_pct > self.max_price_change:
            # Limit the change to maximum allowed
            if recommended_price > current_price:
                return current_price * (1 + self.max_price_change / 100)
            else:
                return current_price * (1 - self.max_price_change / 100)
        
        return recommended_price
    
    async def _analyze_competitors(self, product_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitor pricing"""
        
        competitor_prices = context.get("competitor_prices", {})
        
        if not competitor_prices:
            return {"status": "no_data", "message": "No competitor data available"}
        
        analysis = {
            "total_competitors": len(competitor_prices),
            "competitors": {}
        }
        
        all_prices = []
        for competitor_id, prices in competitor_prices.items():
            if prices:
                latest_price = prices[0]["price"]
                all_prices.append(latest_price)
                analysis["competitors"][competitor_id] = {
                    "latest_price": latest_price,
                    "price_count": len(prices)
                }
        
        if all_prices:
            analysis["market_summary"] = {
                "min_price": min(all_prices),
                "max_price": max(all_prices),
                "avg_price": sum(all_prices) / len(all_prices),
                "price_spread": max(all_prices) - min(all_prices)
            }
        
        return analysis
    
    async def _estimate_impact(self, product_id: str, current_price: float, new_price: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate impact of price change"""
        
        price_change = new_price - current_price
        price_change_pct = (price_change / current_price) * 100
        
        # Simple impact estimation (in a real system, this would use ML models)
        estimated_demand_change = -1.5 * price_change_pct  # Assume elasticity of -1.5
        estimated_revenue_change = price_change_pct + estimated_demand_change
        
        return {
            "price_change": price_change,
            "price_change_percentage": price_change_pct,
            "estimated_demand_change_percentage": estimated_demand_change,
            "estimated_revenue_change_percentage": estimated_revenue_change,
            "risk_level": "high" if abs(price_change_pct) > 10 else "medium" if abs(price_change_pct) > 5 else "low"
        }
    
    async def _get_current_price(self, product_id: str) -> Optional[float]:
        """Get current price for a product (simplified lookup)"""
        
        # In a real implementation, this would call the Product Service
        # For now, we'll look at price history
        recent_history = await PriceHistory.find(
            PriceHistory.product_id == product_id
        ).sort(-PriceHistory.timestamp).limit(1).to_list()
        
        if recent_history:
            return recent_history[0].our_price
        
        # Fallback: return a default price for testing
        return 99.99
