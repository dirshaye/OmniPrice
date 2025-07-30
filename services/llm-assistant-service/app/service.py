import grpc
from app.proto import llm_assistant_service_pb2
from app.proto import llm_assistant_service_pb2_grpc
from app.config import settings
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)

class LLMAssistantService(llm_assistant_service_pb2_grpc.LLMAssistantServiceServicer):
    async def GetPricingAnalysis(self, request, context):
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Analyze the pricing for product {request.product_id} against competitors {', '.join(request.competitor_ids)}."
            response = await model.generate_content_async(prompt)
            
            # This is a mock response, in a real scenario you would parse the llm response
            analysis = llm_assistant_service_pb2.PricingAnalysis(
                product_id=request.product_id,
                analysis_text=response.text,
                suggested_price_min=89.99,
                suggested_price_max=109.99,
                confidence_level="HIGH"
            )
            return llm_assistant_service_pb2.GetPricingAnalysisResponse(analysis=analysis)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return llm_assistant_service_pb2.GetPricingAnalysisResponse()

    async def GetMarketTrends(self, request, context):
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"What are the current market trends for {request.industry} in {request.region}?"
            response = await model.generate_content_async(prompt)
            
            # Mock response
            trend = llm_assistant_service_pb2.MarketTrend(
                trend_id="1",
                trend_description=response.text,
                source="Gemini"
            )
            return llm_assistant_service_pb2.GetMarketTrendsResponse(trends=[trend])
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return llm_assistant_service_pb2.GetMarketTrendsResponse()

    async def GetCompetitorInsights(self, request, context):
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Provide insights on competitor {request.competitor_id}."
            response = await model.generate_content_async(prompt)
            
            # Mock response
            insight = llm_assistant_service_pb2.CompetitorInsight(
                competitor_id=request.competitor_id,
                insight_text=response.text,
                impact_level="MEDIUM"
            )
            return llm_assistant_service_pb2.GetCompetitorInsightsResponse(insights=[insight])
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return llm_assistant_service_pb2.GetCompetitorInsightsResponse()

    async def GetPricingRecommendations(self, request, context):
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Give me {request.number_of_recommendations} pricing recommendations for product {request.product_id}."
            response = await model.generate_content_async(prompt)
            
            # Mock response
            recommendation = llm_assistant_service_pb2.PricingRecommendation(
                product_id=request.product_id,
                recommended_price=99.99,
                justification=response.text
            )
            return llm_assistant_service_pb2.GetPricingRecommendationsResponse(recommendations=[recommendation])
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return llm_assistant_service_pb2.GetPricingRecommendationsResponse()
