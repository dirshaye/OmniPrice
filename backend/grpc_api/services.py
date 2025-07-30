import grpc
from concurrent import futures
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User

# Generated gRPC code (would be generated from .proto file)
# import pricing_pb2
# import pricing_pb2_grpc

from core.models import Product, PricingRule, PricingDecision, PriceHistory, CompetitorProduct
from pricing_engine.engine import PricingEngine

logger = logging.getLogger(__name__)

class PricingServiceServicer:
    """
    gRPC service implementation for pricing operations
    """
    
    def __init__(self):
        self.pricing_engine = PricingEngine()
    
    def RecommendPrice(self, request, context):
        """Get price recommendation for a product"""
        try:
            # Get product
            try:
                product = Product.objects.get(id=request.product_id, is_active=True)
            except Product.DoesNotExist:
                return self._error_response("Product not found")
            
            # Get specific rules if provided
            rules = None
            if request.rule_ids:
                rules = PricingRule.objects.filter(
                    id__in=request.rule_ids,
                    is_active=True
                )
            
            # Generate recommendation
            recommendation = self.pricing_engine.recommend_price(product, rules)
            
            # Build response
            response = {
                'success': True,
                'message': 'Price recommendation generated successfully',
                'recommendation': {
                    'product_id': str(product.id),
                    'current_price': float(product.current_price),
                    'recommended_price': float(recommendation['recommended_price']),
                    'confidence': recommendation['confidence'],
                    'reasoning': recommendation['reasoning'],
                    'applied_rules': recommendation['applied_rules'],
                    'timestamp': recommendation['timestamp'].isoformat(),
                }
            }
            
            # Add competitor analysis if requested
            if request.include_competitor_analysis:
                comp_analysis = recommendation.get('competitor_analysis', {})
                response['recommendation']['competitor_analysis'] = {
                    'competitor_count': comp_analysis.get('competitor_count', 0),
                    'min_price': comp_analysis.get('min_price', 0.0),
                    'max_price': comp_analysis.get('max_price', 0.0),
                    'avg_price': comp_analysis.get('avg_price', 0.0),
                    'our_position': comp_analysis.get('our_position', 'unknown'),
                    'competitor_prices': [
                        {
                            'competitor_name': cp['competitor'],
                            'price': cp['price'],
                            'in_stock': cp['in_stock'],
                            'last_updated': ''  # Would add timestamp
                        }
                        for cp in comp_analysis.get('competitor_prices', [])
                    ]
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RecommendPrice: {str(e)}")
            return self._error_response(f"Internal error: {str(e)}")
    
    def UpdatePrice(self, request, context):
        """Update product price"""
        try:
            # Get product
            try:
                product = Product.objects.get(id=request.product_id, is_active=True)
            except Product.DoesNotExist:
                return self._error_response("Product not found")
            
            # Get user
            user = None
            if request.user_id:
                try:
                    user = User.objects.get(id=request.user_id)
                except User.DoesNotExist:
                    pass
            
            # Validate price
            new_price = request.new_price
            if new_price < float(product.min_price) or new_price > float(product.max_price):
                return self._error_response(
                    f"Price must be between ${product.min_price} and ${product.max_price}"
                )
            
            # Create pricing decision
            decision = PricingDecision.objects.create(
                product=product,
                old_price=product.current_price,
                new_price=new_price,
                decision_source='api',
                reasoning=request.reason or 'Price updated via gRPC API',
                status='approved',
                approved_by=user
            )
            
            # Update product price
            product.current_price = new_price
            product.save()
            
            # Update decision status
            decision.status = 'applied'
            decision.save()
            
            return {
                'success': True,
                'message': 'Price updated successfully',
                'decision_id': str(decision.id)
            }
            
        except Exception as e:
            logger.error(f"Error in UpdatePrice: {str(e)}")
            return self._error_response(f"Internal error: {str(e)}")
    
    def GetPriceHistory(self, request, context):
        """Get price history for a product"""
        try:
            # Get product
            try:
                product = Product.objects.get(id=request.product_id, is_active=True)
            except Product.DoesNotExist:
                return self._error_response("Product not found")
            
            # Calculate date range
            days_back = request.days_back or 30
            start_date = timezone.now() - timedelta(days=days_back)
            
            # Get price history
            history_query = PriceHistory.objects.filter(
                product=product,
                timestamp__gte=start_date
            ).order_by('-timestamp')
            
            entries = []
            for entry in history_query:
                history_entry = {
                    'timestamp': entry.timestamp.isoformat(),
                    'our_price': float(entry.our_price) if entry.our_price else 0.0,
                    'competitor_price': float(entry.competitor_price) if entry.competitor_price else 0.0,
                    'competitor_name': '',
                    'price_change_reason': entry.price_change_reason
                }
                
                if entry.competitor_product:
                    history_entry['competitor_name'] = entry.competitor_product.competitor.name
                
                entries.append(history_entry)
            
            return {
                'success': True,
                'message': 'Price history retrieved successfully',
                'entries': entries
            }
            
        except Exception as e:
            logger.error(f"Error in GetPriceHistory: {str(e)}")
            return self._error_response(f"Internal error: {str(e)}")
    
    def BulkUpdatePrices(self, request, context):
        """Bulk update prices for multiple products"""
        try:
            # Get user
            user = None
            if request.user_id:
                try:
                    user = User.objects.get(id=request.user_id)
                except User.DoesNotExist:
                    pass
            
            # Run bulk optimization
            result = self.pricing_engine.bulk_price_optimization(
                product_ids=list(request.product_ids) if request.product_ids else None
            )
            
            # Auto-apply if requested
            if request.auto_apply:
                pending_decisions = PricingDecision.objects.filter(
                    status='pending',
                    product__id__in=request.product_ids if request.product_ids else []
                )
                
                applied_count = 0
                for decision in pending_decisions:
                    try:
                        # Update product price
                        decision.product.current_price = decision.new_price
                        decision.product.save()
                        
                        # Update decision
                        decision.status = 'applied'
                        decision.approved_by = user
                        decision.save()
                        
                        applied_count += 1
                    except Exception as e:
                        logger.error(f"Error applying decision {decision.id}: {str(e)}")
                
                result['decisions_applied'] = applied_count
            
            return {
                'success': True,
                'message': 'Bulk price optimization completed',
                'total_products': result['total_products'],
                'recommendations_generated': result['recommendations_generated'],
                'decisions_created': result['decisions_created'],
                'errors': result['errors']
            }
            
        except Exception as e:
            logger.error(f"Error in BulkUpdatePrices: {str(e)}")
            return self._error_response(f"Internal error: {str(e)}")
    
    def GetCompetitorAnalysis(self, request, context):
        """Get competitor analysis for a product"""
        try:
            # Get product
            try:
                product = Product.objects.get(id=request.product_id, is_active=True)
            except Product.DoesNotExist:
                return self._error_response("Product not found")
            
            # Generate analysis
            analysis = self.pricing_engine._analyze_competitor_prices(product)
            
            response = {
                'success': True,
                'message': 'Competitor analysis retrieved successfully',
                'analysis': {
                    'competitor_count': analysis['competitor_count'],
                    'min_price': analysis.get('min_price', 0.0),
                    'max_price': analysis.get('max_price', 0.0),
                    'avg_price': analysis.get('avg_price', 0.0),
                    'our_position': analysis['our_position'],
                    'competitor_prices': [
                        {
                            'competitor_name': cp['competitor'],
                            'price': cp['price'],
                            'in_stock': cp['in_stock'],
                            'last_updated': ''  # Would add timestamp
                        }
                        for cp in analysis.get('competitor_prices', [])
                    ]
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error in GetCompetitorAnalysis: {str(e)}")
            return self._error_response(f"Internal error: {str(e)}")
    
    def _error_response(self, message):
        """Helper to create error response"""
        return {
            'success': False,
            'message': message
        }

def serve_grpc(port=50051):
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add service to server
    # pricing_pb2_grpc.add_PricingServiceServicer_to_server(
    #     PricingServiceServicer(), server
    # )
    
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve_grpc()
