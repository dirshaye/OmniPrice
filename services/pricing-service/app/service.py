"""
Pricing Service gRPC Implementation
"""

import grpc
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.empty_pb2 import Empty

# Import proto files directly
import sys
import os
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import pricing_service_pb2
from shared.proto import pricing_service_pb2_grpc

from .database import (
    PricingRule, PricingDecision, PriceHistory,
    RuleType, DecisionStatus, DecisionSource
)
from .pricing_engine import PricingEngine
from .config import settings

logger = logging.getLogger(__name__)

class PricingService(pricing_service_pb2_grpc.PricingServiceServicer):
    """gRPC Pricing Service Implementation"""
    
    def __init__(self):
        self.pricing_engine = PricingEngine()
        logger.info("🎯 Pricing Service initialized")
    
    async def RecommendPrice(self, request, context):
        """Generate price recommendation for a single product"""
        
        try:
            logger.info(f"🎯 Price recommendation request for product: {request.product_id}")
            
            # Get current price - in real implementation, this would call Product Service
            current_price = await self._get_product_current_price(request.product_id)
            if not current_price:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Product {request.product_id} not found")
                return pricing_service_pb2.PriceRecommendationResponse()
            
            # Generate recommendation
            recommendation = await self.pricing_engine.recommend_price(
                product_id=request.product_id,
                current_price=current_price,
                rule_ids=list(request.rule_ids) if request.rule_ids else None,
                include_competitor_analysis=request.include_competitor_analysis,
                include_impact_estimation=request.include_impact_estimation
            )
            
            # Convert to protobuf
            proto_recommendation = pricing_service_pb2.PriceRecommendation(
                product_id=recommendation.product_id,
                current_price=recommendation.current_price,
                recommended_price=recommendation.recommended_price,
                confidence=recommendation.confidence,
                reasoning=recommendation.reasoning,
                applied_rules=recommendation.applied_rules
            )
            
            # Add supporting data
            if recommendation.supporting_data:
                supporting_struct = Struct()
                supporting_struct.update(recommendation.supporting_data)
                proto_recommendation.supporting_data.CopyFrom(supporting_struct)
            
            # Add competitor analysis
            if recommendation.competitor_analysis:
                competitor_struct = Struct()
                competitor_struct.update(recommendation.competitor_analysis)
                proto_recommendation.competitor_analysis.CopyFrom(competitor_struct)
            
            # Add estimated impact
            if recommendation.estimated_impact:
                impact_struct = Struct()
                impact_struct.update(recommendation.estimated_impact)
                proto_recommendation.estimated_impact.CopyFrom(impact_struct)
            
            # Set timestamp
            timestamp = Timestamp()
            timestamp.FromDatetime(recommendation.timestamp)
            proto_recommendation.timestamp.CopyFrom(timestamp)
            
            return pricing_service_pb2.PriceRecommendationResponse(
                success=True,
                message="Price recommendation generated successfully",
                recommendation=proto_recommendation
            )
            
        except Exception as e:
            logger.error(f"Error in RecommendPrice: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.PriceRecommendationResponse(
                success=False,
                message=f"Error generating recommendation: {str(e)}"
            )
    
    async def BulkRecommendPrices(self, request, context):
        """Generate bulk price recommendations"""
        
        try:
            logger.info(f"🎯 Bulk price recommendation for {len(request.product_ids)} products")
            
            recommendations = await self.pricing_engine.bulk_recommend_prices(
                product_ids=list(request.product_ids),
                categories=list(request.categories) if request.categories else None,
                brands=list(request.brands) if request.brands else None,
                rule_ids=list(request.rule_ids) if request.rule_ids else None,
                include_competitor_analysis=request.include_competitor_analysis,
                confidence_threshold=request.confidence_threshold if request.confidence_threshold > 0 else None
            )
            
            # Convert to protobuf
            proto_recommendations = []
            for rec in recommendations:
                proto_rec = pricing_service_pb2.PriceRecommendation(
                    product_id=rec.product_id,
                    current_price=rec.current_price,
                    recommended_price=rec.recommended_price,
                    confidence=rec.confidence,
                    reasoning=rec.reasoning,
                    applied_rules=rec.applied_rules
                )
                
                # Add timestamp
                timestamp = Timestamp()
                timestamp.FromDatetime(rec.timestamp)
                proto_rec.timestamp.CopyFrom(timestamp)
                
                proto_recommendations.append(proto_rec)
            
            return pricing_service_pb2.BulkPriceRecommendationResponse(
                success=True,
                message=f"Generated {len(proto_recommendations)} recommendations",
                recommendations=proto_recommendations,
                total_processed=len(request.product_ids),
                total_recommended=len(proto_recommendations)
            )
            
        except Exception as e:
            logger.error(f"Error in BulkRecommendPrices: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.BulkPriceRecommendationResponse(
                success=False,
                message=f"Error generating bulk recommendations: {str(e)}"
            )
    
    async def CreatePricingRule(self, request, context):
        """Create a new pricing rule"""
        
        try:
            logger.info(f"📋 Creating pricing rule: {request.name}")
            
            # Convert protobuf Struct to dict
            parameters = {}
            if request.parameters:
                parameters = dict(request.parameters)
            
            conditions = {}
            if request.conditions:
                conditions = dict(request.conditions)
            
            # Create rule
            rule = PricingRule(
                name=request.name,
                description=request.description,
                rule_type=RuleType(request.rule_type),
                product_ids=list(request.product_ids),
                categories=list(request.categories),
                brands=list(request.brands),
                tags=list(request.tags),
                parameters=parameters,
                conditions=conditions,
                priority=request.priority,
                schedule_enabled=request.schedule_enabled,
                schedule_cron=request.schedule_cron if request.schedule_cron else None,
                timezone=request.timezone if request.timezone else "UTC",
                created_by=request.created_by
            )
            
            await rule.insert()
            
            # Convert back to protobuf
            proto_rule = await self._convert_rule_to_proto(rule)
            
            return pricing_service_pb2.PricingRuleResponse(
                success=True,
                message="Pricing rule created successfully",
                rule=proto_rule
            )
            
        except Exception as e:
            logger.error(f"Error creating pricing rule: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.PricingRuleResponse(
                success=False,
                message=f"Error creating rule: {str(e)}"
            )
    
    async def GetPricingRule(self, request, context):
        """Get a specific pricing rule"""
        
        try:
            rule = await PricingRule.get(request.id)
            if not rule:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Pricing rule not found")
                return pricing_service_pb2.PricingRuleResponse()
            
            proto_rule = await self._convert_rule_to_proto(rule)
            
            return pricing_service_pb2.PricingRuleResponse(
                success=True,
                message="Pricing rule retrieved successfully",
                rule=proto_rule
            )
            
        except Exception as e:
            logger.error(f"Error getting pricing rule: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.PricingRuleResponse()
    
    async def UpdatePricingRule(self, request, context):
        """Update an existing pricing rule"""
        
        try:
            rule = await PricingRule.get(request.id)
            if not rule:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Pricing rule not found")
                return pricing_service_pb2.PricingRuleResponse()
            
            # Update fields
            update_data = {"updated_at": datetime.utcnow()}
            
            if request.HasField("name"):
                update_data["name"] = request.name
            if request.HasField("description"):
                update_data["description"] = request.description
            if request.product_ids:
                update_data["product_ids"] = list(request.product_ids)
            if request.categories:
                update_data["categories"] = list(request.categories)
            if request.brands:
                update_data["brands"] = list(request.brands)
            if request.tags:
                update_data["tags"] = list(request.tags)
            if request.parameters:
                update_data["parameters"] = dict(request.parameters)
            if request.conditions:
                update_data["conditions"] = dict(request.conditions)
            if request.HasField("is_active"):
                update_data["is_active"] = request.is_active
            if request.HasField("priority"):
                update_data["priority"] = request.priority
            if request.HasField("schedule_enabled"):
                update_data["schedule_enabled"] = request.schedule_enabled
            if request.HasField("schedule_cron"):
                update_data["schedule_cron"] = request.schedule_cron
            if request.HasField("timezone"):
                update_data["timezone"] = request.timezone
            
            await rule.update({"$set": update_data})
            
            # Fetch updated rule
            updated_rule = await PricingRule.get(request.id)
            proto_rule = await self._convert_rule_to_proto(updated_rule)
            
            return pricing_service_pb2.PricingRuleResponse(
                success=True,
                message="Pricing rule updated successfully",
                rule=proto_rule
            )
            
        except Exception as e:
            logger.error(f"Error updating pricing rule: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.PricingRuleResponse()
    
    async def DeletePricingRule(self, request, context):
        """Delete a pricing rule"""
        
        try:
            rule = await PricingRule.get(request.id)
            if not rule:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Pricing rule not found")
                return Empty()
            
            await rule.delete()
            
            logger.info(f"📋 Deleted pricing rule: {rule.name}")
            return Empty()
            
        except Exception as e:
            logger.error(f"Error deleting pricing rule: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return Empty()
    
    async def ListPricingRules(self, request, context):
        """List pricing rules with pagination"""
        
        try:
            # Build query
            query = {}
            if request.HasField("rule_type"):
                query["rule_type"] = request.rule_type
            if request.HasField("is_active"):
                query["is_active"] = request.is_active
            
            # Get total count
            total = await PricingRule.find(query).count()
            
            # Apply pagination
            page = max(1, request.page)
            limit = min(100, max(1, request.limit))  # Limit between 1-100
            skip = (page - 1) * limit
            
            # Fetch rules
            rules = await PricingRule.find(query).sort(-PricingRule.priority).skip(skip).limit(limit).to_list()
            
            # Convert to protobuf
            proto_rules = []
            for rule in rules:
                proto_rule = await self._convert_rule_to_proto(rule)
                proto_rules.append(proto_rule)
            
            has_next = (skip + limit) < total
            
            return pricing_service_pb2.ListPricingRulesResponse(
                rules=proto_rules,
                total=total,
                page=page,
                limit=limit,
                has_next=has_next
            )
            
        except Exception as e:
            logger.error(f"Error listing pricing rules: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.ListPricingRulesResponse()
    
    async def ExecutePricingRule(self, request, context):
        """Execute a pricing rule and create decisions"""
        
        try:
            logger.info(f"⚡ Executing pricing rule: {request.rule_id}")
            
            rule = await PricingRule.get(request.rule_id)
            if not rule:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Pricing rule not found")
                return pricing_service_pb2.ExecutePricingRuleResponse()
            
            # Get products to process
            product_ids = list(request.product_ids) if request.product_ids else await self._get_rule_products(rule)
            
            decisions_created = 0
            decisions_applied = 0
            error_messages = []
            
            # Process each product
            for product_id in product_ids:
                try:
                    # Get current price
                    current_price = await self._get_product_current_price(product_id)
                    if not current_price:
                        error_messages.append(f"Product {product_id}: price not found")
                        continue
                    
                    # Generate recommendation
                    recommendation = await self.pricing_engine.recommend_price(
                        product_id=product_id,
                        current_price=current_price,
                        rule_ids=[str(rule.id)]
                    )
                    
                    # Create pricing decision
                    decision = PricingDecision(
                        product_id=product_id,
                        product_name=f"Product {product_id}",  # In real implementation, get from Product Service
                        product_sku=f"SKU-{product_id}",
                        old_price=current_price,
                        new_price=recommendation.recommended_price,
                        price_change=recommendation.recommended_price - current_price,
                        price_change_percentage=((recommendation.recommended_price - current_price) / current_price) * 100,
                        decision_source=DecisionSource.RULE_ENGINE,
                        applied_rule_id=str(rule.id),
                        applied_rule_name=rule.name,
                        confidence_score=recommendation.confidence,
                        reasoning=recommendation.reasoning,
                        supporting_data=recommendation.supporting_data,
                        status=DecisionStatus.APPROVED if request.auto_apply else DecisionStatus.PENDING
                    )
                    
                    if request.auto_apply:
                        decision.approved_by = request.executed_by
                        decision.approved_at = datetime.utcnow()
                        decision.applied_at = datetime.utcnow()
                        decisions_applied += 1
                    
                    await decision.insert()
                    decisions_created += 1
                    
                except Exception as e:
                    error_messages.append(f"Product {product_id}: {str(e)}")
            
            # Update rule execution stats
            await rule.update({
                "$set": {
                    "last_executed": datetime.utcnow(),
                    "execution_count": rule.execution_count + 1,
                    "success_count": rule.success_count + (1 if not error_messages else 0)
                }
            })
            
            return pricing_service_pb2.ExecutePricingRuleResponse(
                success=True,
                message=f"Rule executed successfully. Created {decisions_created} decisions, applied {decisions_applied}",
                total_processed=len(product_ids),
                decisions_created=decisions_created,
                decisions_applied=decisions_applied,
                error_messages=error_messages
            )
            
        except Exception as e:
            logger.error(f"Error executing pricing rule: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.ExecutePricingRuleResponse(
                success=False,
                message=f"Error executing rule: {str(e)}"
            )
    
    async def CreatePricingDecision(self, request, context):
        """Create a new pricing decision"""
        
        try:
            # Convert supporting data
            supporting_data = {}
            if request.supporting_data:
                supporting_data = dict(request.supporting_data)
            
            decision = PricingDecision(
                product_id=request.product_id,
                product_name=f"Product {request.product_id}",  # Get from Product Service in real implementation
                product_sku=f"SKU-{request.product_id}",
                old_price=request.old_price,
                new_price=request.new_price,
                price_change=request.new_price - request.old_price,
                price_change_percentage=((request.new_price - request.old_price) / request.old_price) * 100,
                decision_source=DecisionSource(request.decision_source),
                applied_rule_id=request.applied_rule_id if request.applied_rule_id else None,
                confidence_score=request.confidence_score,
                reasoning=request.reasoning,
                supporting_data=supporting_data
            )
            
            await decision.insert()
            
            proto_decision = await self._convert_decision_to_proto(decision)
            
            return pricing_service_pb2.PricingDecisionResponse(
                success=True,
                message="Pricing decision created successfully",
                decision=proto_decision
            )
            
        except Exception as e:
            logger.error(f"Error creating pricing decision: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.PricingDecisionResponse(
                success=False,
                message=f"Error creating decision: {str(e)}"
            )
    
    async def ApprovePricingDecision(self, request, context):
        """Approve a pricing decision"""
        
        try:
            decision = await PricingDecision.get(request.decision_id)
            if not decision:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Pricing decision not found")
                return pricing_service_pb2.PricingDecisionResponse()
            
            # Update decision
            await decision.update({
                "$set": {
                    "status": DecisionStatus.APPROVED,
                    "approved_by": request.approved_by,
                    "approved_at": datetime.utcnow()
                }
            })
            
            # Fetch updated decision
            updated_decision = await PricingDecision.get(request.decision_id)
            proto_decision = await self._convert_decision_to_proto(updated_decision)
            
            return pricing_service_pb2.PricingDecisionResponse(
                success=True,
                message="Pricing decision approved successfully",
                decision=proto_decision
            )
            
        except Exception as e:
            logger.error(f"Error approving pricing decision: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.PricingDecisionResponse()
    
    async def RejectPricingDecision(self, request, context):
        """Reject a pricing decision"""
        
        try:
            decision = await PricingDecision.get(request.decision_id)
            if not decision:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Pricing decision not found")
                return pricing_service_pb2.PricingDecisionResponse()
            
            # Update decision
            await decision.update({
                "$set": {
                    "status": DecisionStatus.REJECTED,
                    "rejection_reason": request.rejection_reason
                }
            })
            
            # Fetch updated decision
            updated_decision = await PricingDecision.get(request.decision_id)
            proto_decision = await self._convert_decision_to_proto(updated_decision)
            
            return pricing_service_pb2.PricingDecisionResponse(
                success=True,
                message="Pricing decision rejected successfully",
                decision=proto_decision
            )
            
        except Exception as e:
            logger.error(f"Error rejecting pricing decision: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.PricingDecisionResponse()
    
    async def ListPricingDecisions(self, request, context):
        """List pricing decisions with pagination"""
        
        try:
            # Build query
            query = {}
            if request.HasField("product_id"):
                query["product_id"] = request.product_id
            if request.HasField("status"):
                query["status"] = request.status
            if request.HasField("decision_source"):
                query["decision_source"] = request.decision_source
            
            # Get total count
            total = await PricingDecision.find(query).count()
            
            # Apply pagination
            page = max(1, request.page)
            limit = min(100, max(1, request.limit))
            skip = (page - 1) * limit
            
            # Fetch decisions
            decisions = await PricingDecision.find(query).sort(-PricingDecision.timestamp).skip(skip).limit(limit).to_list()
            
            # Convert to protobuf
            proto_decisions = []
            for decision in decisions:
                proto_decision = await self._convert_decision_to_proto(decision)
                proto_decisions.append(proto_decision)
            
            has_next = (skip + limit) < total
            
            return pricing_service_pb2.ListPricingDecisionsResponse(
                decisions=proto_decisions,
                total=total,
                page=page,
                limit=limit,
                has_next=has_next
            )
            
        except Exception as e:
            logger.error(f"Error listing pricing decisions: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.ListPricingDecisionsResponse()
    
    async def GetPriceHistory(self, request, context):
        """Get price history for a product"""
        
        try:
            # Build query
            query = {"product_id": request.product_id}
            
            # Date range filter
            if request.days_back > 0:
                cutoff_date = datetime.utcnow() - timedelta(days=request.days_back)
                query["timestamp"] = {"$gte": cutoff_date}
            
            # Get total count
            total = await PriceHistory.find(query).count()
            
            # Apply pagination
            page = max(1, request.page)
            limit = min(100, max(1, request.limit))
            skip = (page - 1) * limit
            
            # Fetch history
            history_entries = await PriceHistory.find(query).sort(-PriceHistory.timestamp).skip(skip).limit(limit).to_list()
            
            # Convert to protobuf
            proto_entries = []
            for entry in history_entries:
                proto_entry = await self._convert_history_to_proto(entry)
                proto_entries.append(proto_entry)
            
            has_next = (skip + limit) < total
            
            return pricing_service_pb2.GetPriceHistoryResponse(
                success=True,
                message=f"Retrieved {len(proto_entries)} price history entries",
                entries=proto_entries,
                total=total,
                page=page,
                limit=limit,
                has_next=has_next
            )
            
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.GetPriceHistoryResponse(
                success=False,
                message=f"Error retrieving price history: {str(e)}"
            )
    
    async def RecordPriceChange(self, request, context):
        """Record a price change in history"""
        
        try:
            # Convert market conditions
            market_conditions = {}
            if request.market_conditions:
                market_conditions = dict(request.market_conditions)
            
            # Calculate price difference
            price_difference = None
            price_difference_percentage = None
            if request.competitor_price > 0:
                price_difference = request.our_price - request.competitor_price
                price_difference_percentage = (price_difference / request.competitor_price) * 100
            
            history_entry = PriceHistory(
                product_id=request.product_id,
                product_sku=request.product_sku,
                competitor_id=request.competitor_id if request.competitor_id else None,
                competitor_name=request.competitor_name if request.competitor_name else None,
                our_price=request.our_price,
                competitor_price=request.competitor_price if request.competitor_price > 0 else None,
                price_difference=price_difference,
                price_difference_percentage=price_difference_percentage,
                reason=request.reason,
                market_conditions=market_conditions,
                notes=request.notes if request.notes else None
            )
            
            await history_entry.insert()
            
            logger.info(f"📊 Recorded price change for product {request.product_id}")
            return Empty()
            
        except Exception as e:
            logger.error(f"Error recording price change: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return Empty()
    
    # Helper methods
    
    async def _convert_rule_to_proto(self, rule: PricingRule) -> pricing_service_pb2.PricingRule:
        """Convert database rule to protobuf"""
        
        proto_rule = pricing_service_pb2.PricingRule(
            id=str(rule.id),
            name=rule.name,
            description=rule.description,
            rule_type=rule.rule_type.value,
            product_ids=rule.product_ids,
            categories=rule.categories,
            brands=rule.brands,
            tags=rule.tags,
            is_active=rule.is_active,
            priority=rule.priority,
            schedule_enabled=rule.schedule_enabled,
            schedule_cron=rule.schedule_cron or "",
            timezone=rule.timezone,
            execution_count=rule.execution_count,
            success_count=rule.success_count,
            created_by=rule.created_by
        )
        
        # Add parameters
        if rule.parameters:
            params_struct = Struct()
            params_struct.update(rule.parameters)
            proto_rule.parameters.CopyFrom(params_struct)
        
        # Add conditions
        if rule.conditions:
            conditions_struct = Struct()
            conditions_struct.update(rule.conditions)
            proto_rule.conditions.CopyFrom(conditions_struct)
        
        # Add timestamps
        if rule.last_executed:
            last_exec_timestamp = Timestamp()
            last_exec_timestamp.FromDatetime(rule.last_executed)
            proto_rule.last_executed.CopyFrom(last_exec_timestamp)
        
        created_timestamp = Timestamp()
        created_timestamp.FromDatetime(rule.created_at)
        proto_rule.created_at.CopyFrom(created_timestamp)
        
        updated_timestamp = Timestamp()
        updated_timestamp.FromDatetime(rule.updated_at)
        proto_rule.updated_at.CopyFrom(updated_timestamp)
        
        return proto_rule
    
    async def _convert_decision_to_proto(self, decision: PricingDecision) -> pricing_service_pb2.PricingDecision:
        """Convert database decision to protobuf"""
        
        proto_decision = pricing_service_pb2.PricingDecision(
            id=str(decision.id),
            product_id=decision.product_id,
            product_name=decision.product_name,
            product_sku=decision.product_sku,
            old_price=decision.old_price,
            new_price=decision.new_price,
            price_change=decision.price_change,
            price_change_percentage=decision.price_change_percentage,
            decision_source=decision.decision_source.value,
            applied_rule_id=decision.applied_rule_id or "",
            applied_rule_name=decision.applied_rule_name or "",
            confidence_score=decision.confidence_score,
            reasoning=decision.reasoning,
            status=decision.status.value,
            approved_by=decision.approved_by or "",
            rejection_reason=decision.rejection_reason or ""
        )
        
        # Add supporting data
        if decision.supporting_data:
            supporting_struct = Struct()
            supporting_struct.update(decision.supporting_data)
            proto_decision.supporting_data.CopyFrom(supporting_struct)
        
        # Add timestamps
        if decision.approved_at:
            approved_timestamp = Timestamp()
            approved_timestamp.FromDatetime(decision.approved_at)
            proto_decision.approved_at.CopyFrom(approved_timestamp)
        
        if decision.applied_at:
            applied_timestamp = Timestamp()
            applied_timestamp.FromDatetime(decision.applied_at)
            proto_decision.applied_at.CopyFrom(applied_timestamp)
        
        timestamp = Timestamp()
        timestamp.FromDatetime(decision.timestamp)
        proto_decision.timestamp.CopyFrom(timestamp)
        
        return proto_decision
    
    async def _convert_history_to_proto(self, history: PriceHistory) -> pricing_service_pb2.PriceHistory:
        """Convert database history to protobuf"""
        
        proto_history = pricing_service_pb2.PriceHistory(
            id=str(history.id),
            product_id=history.product_id,
            product_sku=history.product_sku,
            competitor_id=history.competitor_id or "",
            competitor_name=history.competitor_name or "",
            our_price=history.our_price,
            competitor_price=history.competitor_price or 0.0,
            price_difference=history.price_difference or 0.0,
            price_difference_percentage=history.price_difference_percentage or 0.0,
            reason=history.reason,
            notes=history.notes or ""
        )
        
        # Add market conditions
        if history.market_conditions:
            conditions_struct = Struct()
            conditions_struct.update(history.market_conditions)
            proto_history.market_conditions.CopyFrom(conditions_struct)
        
        # Add timestamp
        timestamp = Timestamp()
        timestamp.FromDatetime(history.timestamp)
        proto_history.timestamp.CopyFrom(timestamp)
        
        return proto_history
    
    async def _get_product_current_price(self, product_id: str) -> Optional[float]:
        """Get current price for a product"""
        
        # In a real implementation, this would call the Product Service
        # For now, we'll use price history or return a default
        
        recent_history = await PriceHistory.find(
            PriceHistory.product_id == product_id
        ).sort(-PriceHistory.timestamp).limit(1).to_list()
        
        if recent_history:
            return recent_history[0].our_price
        
        # Fallback for testing
        return 99.99
    
    async def _get_rule_products(self, rule: PricingRule) -> List[str]:
        """Get list of products that a rule applies to"""
        
        if rule.product_ids:
            return rule.product_ids
        
        # If no specific products, we'd normally query the Product Service
        # For now, return some test product IDs
        return ["PROD_001", "PROD_002", "PROD_003"]
