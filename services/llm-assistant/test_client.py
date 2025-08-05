#!/usr/bin/env python3
"""
Simple gRPC client to test LLM Assistant Service
"""

import asyncio
import grpc
import logging
import sys

# Add project root to path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import llm_assistant_service_pb2
from shared.proto import llm_assistant_service_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_llm_service():
    """Test the LLM service via gRPC"""
    
    # Connect to the server
    async with grpc.aio.insecure_channel('localhost:8002') as channel:
        stub = llm_assistant_service_pb2_grpc.LLMAssistantServiceStub(channel)
        
        logger.info("🔌 Connected to LLM Assistant Service on localhost:8002")
        
        # Test 1: GetPricingAnalysis
        logger.info("\n🧪 Test 1: GetPricingAnalysis")
        request = llm_assistant_service_pb2.GetPricingAnalysisRequest(
            product_id="TEST_PRODUCT_123",
            competitor_ids=["COMP_A", "COMP_B"]
        )
        
        try:
            response = await stub.GetPricingAnalysis(request)
            logger.info("✅ GetPricingAnalysis - Success")
            logger.info(f"Product ID: {response.analysis.product_id}")
            logger.info(f"Analysis: {response.analysis.analysis_text[:100]}...")
            logger.info(f"Suggested Price Range: ${response.analysis.suggested_price_min} - ${response.analysis.suggested_price_max}")
        except Exception as e:
            logger.error(f"❌ GetPricingAnalysis failed: {e}")
        
        # Test 2: GetMarketTrends
        logger.info("\n🧪 Test 2: GetMarketTrends")
        request = llm_assistant_service_pb2.GetMarketTrendsRequest(
            industry="electronics",
            region="North America"
        )
        
        try:
            response = await stub.GetMarketTrends(request)
            logger.info("✅ GetMarketTrends - Success")
            logger.info(f"Number of trends: {len(response.trends)}")
            if response.trends:
                logger.info(f"First trend: {response.trends[0].trend_description[:100]}...")
        except Exception as e:
            logger.error(f"❌ GetMarketTrends failed: {e}")
        
        # Test 3: GetCompetitorInsights
        logger.info("\n🧪 Test 3: GetCompetitorInsights")
        request = llm_assistant_service_pb2.GetCompetitorInsightsRequest(
            competitor_id="COMPETITOR_XYZ"
        )
        
        try:
            response = await stub.GetCompetitorInsights(request)
            logger.info("✅ GetCompetitorInsights - Success")
            logger.info(f"Number of insights: {len(response.insights)}")
            if response.insights:
                logger.info(f"Insight: {response.insights[0].insight_text[:100]}...")
        except Exception as e:
            logger.error(f"❌ GetCompetitorInsights failed: {e}")
        
        # Test 4: GetPricingRecommendations
        logger.info("\n🧪 Test 4: GetPricingRecommendations")
        request = llm_assistant_service_pb2.GetPricingRecommendationsRequest(
            product_id="PRODUCT_ABC"
        )
        
        try:
            response = await stub.GetPricingRecommendations(request)
            logger.info("✅ GetPricingRecommendations - Success")
            logger.info(f"Number of recommendations: {len(response.recommendations)}")
            if response.recommendations:
                logger.info(f"Recommended Price: ${response.recommendations[0].recommended_price}")
                logger.info(f"Justification: {response.recommendations[0].justification[:100]}...")
        except Exception as e:
            logger.error(f"❌ GetPricingRecommendations failed: {e}")

if __name__ == '__main__':
    logger.info("🚀 Starting LLM Assistant Service Client Test")
    asyncio.run(test_llm_service())
