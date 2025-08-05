#!/usr/bin/env python3
"""
Simple gRPC client to test Pricing Service
"""

import asyncio
import grpc
import logging
import sys
from datetime import datetime
from google.protobuf.struct_pb2 import Struct

# Add project root to path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import pricing_service_pb2
from shared.proto import pricing_service_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pricing_service():
    """Test the Pricing Service via gRPC"""
    
    # Connect to the server
    async with grpc.aio.insecure_channel('localhost:50052') as channel:
        stub = pricing_service_pb2_grpc.PricingServiceStub(channel)
        
        logger.info("🔌 Connected to Pricing Service on localhost:50052")
        
        # Test 1: Create a pricing rule
        logger.info("\n🧪 Test 1: CreatePricingRule")
        
        # Create rule parameters
        parameters = Struct()
        parameters.update({
            "strategy": "match_average",
            "margin": 5.0,
            "target_margin_percentage": 20.0
        })
        
        conditions = Struct()
        conditions.update({
            "min_confidence": 0.7,
            "max_price_change": 15.0
        })
        
        create_request = pricing_service_pb2.CreatePricingRuleRequest(
            name="Competitor-Based Pricing",
            description="Price matching with 5% margin above average competitor price",
            rule_type="competitor_based",
            product_ids=["PROD_001", "PROD_002", "PROD_003"],
            categories=["electronics", "gadgets"],
            brands=["TechBrand"],
            parameters=parameters,
            conditions=conditions,
            priority=10,
            schedule_enabled=False,
            created_by="test_user"
        )
        
        try:
            response = await stub.CreatePricingRule(create_request)
            if response.success:
                logger.info("✅ CreatePricingRule - Success")
                logger.info(f"Rule ID: {response.rule.id}")
                logger.info(f"Rule Name: {response.rule.name}")
                logger.info(f"Rule Type: {response.rule.rule_type}")
                rule_id = response.rule.id
            else:
                logger.error(f"❌ CreatePricingRule failed: {response.message}")
                return
        except Exception as e:
            logger.error(f"❌ CreatePricingRule failed: {e}")
            return
        
        # Test 2: List pricing rules
        logger.info("\n🧪 Test 2: ListPricingRules")
        list_request = pricing_service_pb2.ListPricingRulesRequest(
            page=1,
            limit=10
        )
        
        try:
            response = await stub.ListPricingRules(list_request)
            logger.info("✅ ListPricingRules - Success")
            logger.info(f"Total rules: {response.total}")
            for rule in response.rules:
                logger.info(f"  - {rule.name} ({rule.rule_type}) - Priority: {rule.priority}")
        except Exception as e:
            logger.error(f"❌ ListPricingRules failed: {e}")
        
        # Test 3: Record some price history
        logger.info("\n🧪 Test 3: RecordPriceChange")
        
        market_conditions = Struct()
        market_conditions.update({
            "season": "holiday",
            "demand": "high",
            "inventory_level": "low"
        })
        
        price_change_request = pricing_service_pb2.RecordPriceChangeRequest(
            product_id="PROD_001",
            product_sku="SKU-PROD-001",
            competitor_id="COMP_A",
            competitor_name="Competitor A",
            our_price=99.99,
            competitor_price=105.99,
            reason="Regular price monitoring",
            market_conditions=market_conditions,
            notes="Holiday pricing season"
        )
        
        try:
            await stub.RecordPriceChange(price_change_request)
            logger.info("✅ RecordPriceChange - Success")
        except Exception as e:
            logger.error(f"❌ RecordPriceChange failed: {e}")
        
        # Test 4: Get price recommendation
        logger.info("\n🧪 Test 4: RecommendPrice")
        recommend_request = pricing_service_pb2.PriceRecommendationRequest(
            product_id="PROD_001",
            include_competitor_analysis=True,
            include_impact_estimation=True
        )
        
        try:
            response = await stub.RecommendPrice(recommend_request)
            if response.success:
                logger.info("✅ RecommendPrice - Success")
                rec = response.recommendation
                logger.info(f"Product: {rec.product_id}")
                logger.info(f"Current Price: ${rec.current_price:.2f}")
                logger.info(f"Recommended Price: ${rec.recommended_price:.2f}")
                logger.info(f"Confidence: {rec.confidence:.2f}")
                logger.info(f"Reasoning: {rec.reasoning}")
                logger.info(f"Applied Rules: {rec.applied_rules}")
            else:
                logger.error(f"❌ RecommendPrice failed: {response.message}")
        except Exception as e:
            logger.error(f"❌ RecommendPrice failed: {e}")
        
        # Test 5: Get price history
        logger.info("\n🧪 Test 5: GetPriceHistory")
        history_request = pricing_service_pb2.GetPriceHistoryRequest(
            product_id="PROD_001",
            days_back=30,
            include_competitor_prices=True,
            page=1,
            limit=10
        )
        
        try:
            response = await stub.GetPriceHistory(history_request)
            if response.success:
                logger.info("✅ GetPriceHistory - Success")
                logger.info(f"Total entries: {response.total}")
                for entry in response.entries:
                    logger.info(f"  - {entry.timestamp.ToDatetime().strftime('%Y-%m-%d %H:%M')} - Our: ${entry.our_price:.2f}, Competitor: ${entry.competitor_price:.2f}")
            else:
                logger.error(f"❌ GetPriceHistory failed: {response.message}")
        except Exception as e:
            logger.error(f"❌ GetPriceHistory failed: {e}")
        
        # Test 6: Execute pricing rule
        logger.info("\n🧪 Test 6: ExecutePricingRule")
        execute_request = pricing_service_pb2.ExecutePricingRuleRequest(
            rule_id=rule_id,
            product_ids=["PROD_001", "PROD_002"],
            auto_apply=False,  # Don't auto-apply for testing
            executed_by="test_user"
        )
        
        try:
            response = await stub.ExecutePricingRule(execute_request)
            if response.success:
                logger.info("✅ ExecutePricingRule - Success")
                logger.info(f"Processed: {response.total_processed}")
                logger.info(f"Decisions Created: {response.decisions_created}")
                logger.info(f"Decisions Applied: {response.decisions_applied}")
                if response.error_messages:
                    logger.info(f"Errors: {response.error_messages}")
            else:
                logger.error(f"❌ ExecutePricingRule failed: {response.message}")
        except Exception as e:
            logger.error(f"❌ ExecutePricingRule failed: {e}")
        
        # Test 7: List pricing decisions
        logger.info("\n🧪 Test 7: ListPricingDecisions")
        decisions_request = pricing_service_pb2.ListPricingDecisionsRequest(
            page=1,
            limit=10
        )
        
        try:
            response = await stub.ListPricingDecisions(decisions_request)
            logger.info("✅ ListPricingDecisions - Success")
            logger.info(f"Total decisions: {response.total}")
            for decision in response.decisions:
                logger.info(f"  - {decision.product_id}: ${decision.old_price:.2f} → ${decision.new_price:.2f} ({decision.status})")
        except Exception as e:
            logger.error(f"❌ ListPricingDecisions failed: {e}")
        
        # Test 8: Bulk price recommendations
        logger.info("\n🧪 Test 8: BulkRecommendPrices")
        bulk_request = pricing_service_pb2.BulkPriceRecommendationRequest(
            product_ids=["PROD_001", "PROD_002", "PROD_003"],
            include_competitor_analysis=False,  # Skip for faster bulk processing
            confidence_threshold=0.5
        )
        
        try:
            response = await stub.BulkRecommendPrices(bulk_request)
            if response.success:
                logger.info("✅ BulkRecommendPrices - Success")
                logger.info(f"Processed: {response.total_processed}")
                logger.info(f"Recommended: {response.total_recommended}")
                for rec in response.recommendations:
                    logger.info(f"  - {rec.product_id}: ${rec.current_price:.2f} → ${rec.recommended_price:.2f} (conf: {rec.confidence:.2f})")
            else:
                logger.error(f"❌ BulkRecommendPrices failed: {response.message}")
        except Exception as e:
            logger.error(f"❌ BulkRecommendPrices failed: {e}")

if __name__ == '__main__':
    logger.info("🚀 Starting Pricing Service Client Test")
    asyncio.run(test_pricing_service())
