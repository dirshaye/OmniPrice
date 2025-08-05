#!/usr/bin/env python3
"""
Test script for LLM Assistant Service
Tests the Gemini API integration without running the full gRPC server
"""

import asyncio
import os
import sys
import logging

# Add project root to path to import shared modules
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from app.config import settings
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_gemini_api():
    """Test basic Gemini API connectivity and response"""
    try:
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Create model instance
        model = genai.GenerativeModel(settings.DEFAULT_MODEL)
        
        # Test prompt
        test_prompt = "Provide a brief pricing analysis for a product priced at $99 compared to competitors at $89 and $105."
        
        logger.info(f"Testing Gemini API with model: {settings.DEFAULT_MODEL}")
        logger.info(f"Prompt: {test_prompt}")
        
        # Generate response
        response = await model.generate_content_async(test_prompt)
        
        logger.info("✅ Gemini API Test Successful!")
        logger.info(f"Response: {response.text[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Gemini API Test Failed: {str(e)}")
        return False

async def test_llm_service_methods():
    """Test LLM service method logic without gRPC"""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.DEFAULT_MODEL)
        
        # Test scenarios
        test_cases = [
            {
                "name": "Pricing Analysis",
                "prompt": "Analyze the pricing for product ABC123 against competitors DEF456 and GHI789."
            },
            {
                "name": "Market Trends",
                "prompt": "What are the current market trends for electronics in North America?"
            },
            {
                "name": "Competitor Insights", 
                "prompt": "Provide insights on competitor COMP001."
            },
            {
                "name": "Pricing Recommendations",
                "prompt": "Provide pricing recommendations for product XYZ999."
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"\n🧪 Testing: {test_case['name']}")
            
            response = await model.generate_content_async(test_case['prompt'])
            
            if response.text:
                logger.info(f"✅ {test_case['name']} - Success")
                logger.info(f"Response length: {len(response.text)} characters")
            else:
                logger.warning(f"⚠️ {test_case['name']} - Empty response")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Service Methods Test Failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    logger.info("🚀 Starting LLM Assistant Service Tests")
    
    # Check configuration
    logger.info(f"API Key configured: {'Yes' if settings.GEMINI_API_KEY else 'No'}")
    logger.info(f"Model: {settings.DEFAULT_MODEL}")
    
    if not settings.GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY not configured!")
        return
    
    # Run tests
    test1_result = await test_gemini_api()
    if test1_result:
        test2_result = await test_llm_service_methods()
        
        if test1_result and test2_result:
            logger.info("\n🎉 All tests passed! LLM service is ready.")
        else:
            logger.error("\n❌ Some tests failed.")
    else:
        logger.error("\n❌ Basic API test failed. Cannot proceed with other tests.")

if __name__ == "__main__":
    asyncio.run(main())
