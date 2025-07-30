from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.http import JsonResponse
import logging

from core.models import Product, Competitor, PricingRule, PricingDecision, PriceHistory
from .serializers import (
    ProductSerializer, CompetitorSerializer, PricingRuleSerializer,
    PricingDecisionSerializer, PriceHistorySerializer
)
from pricing_engine.engine import PricingEngine
from metrics.collectors import MetricsCollector, APITimer

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product CRUD operations"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        with APITimer('GET', '/api/products/'):
            return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        with APITimer('GET', f'/api/products/{kwargs.get("pk")}/'):
            return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def recommend_price(self, request, pk=None):
        """Get price recommendation for a product"""
        with APITimer('POST', f'/api/products/{pk}/recommend_price/') as timer:
            try:
                product = self.get_object()
                pricing_engine = PricingEngine()
                
                recommendation = pricing_engine.recommend_price(product)
                
                timer.set_status_code(200)
                return Response({
                    'success': True,
                    'recommendation': {
                        'current_price': float(product.current_price),
                        'recommended_price': float(recommendation['recommended_price']),
                        'confidence': recommendation['confidence'],
                        'reasoning': recommendation['reasoning'],
                        'applied_rules': recommendation['applied_rules']
                    }
                })
                
            except Exception as e:
                logger.error(f"Error generating price recommendation: {str(e)}")
                timer.set_status_code(500)
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        """Update product price"""
        with APITimer('POST', f'/api/products/{pk}/update_price/') as timer:
            try:
                product = self.get_object()
                new_price = request.data.get('new_price')
                reason = request.data.get('reason', 'Manual price update')
                
                if not new_price:
                    timer.set_status_code(400)
                    return Response({
                        'success': False,
                        'error': 'new_price is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate price bounds
                if float(new_price) < float(product.min_price) or float(new_price) > float(product.max_price):
                    timer.set_status_code(400)
                    return Response({
                        'success': False,
                        'error': f'Price must be between {product.min_price} and {product.max_price}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create pricing decision
                decision = PricingDecision.objects.create(
                    product=product,
                    old_price=product.current_price,
                    new_price=new_price,
                    decision_source='manual',
                    reasoning=reason,
                    status='approved',
                    approved_by=request.user
                )
                
                # Update product price
                old_price = float(product.current_price)
                product.current_price = new_price
                product.save()
                
                # Update decision status
                decision.status = 'applied'
                decision.save()
                
                # Record metrics
                MetricsCollector.record_pricing_decision('manual', 'applied')
                MetricsCollector.record_price_change(product.category, old_price, float(new_price))
                
                timer.set_status_code(200)
                return Response({
                    'success': True,
                    'decision_id': str(decision.id),
                    'old_price': old_price,
                    'new_price': float(new_price)
                })
                
            except Exception as e:
                logger.error(f"Error updating price: {str(e)}")
                timer.set_status_code(500)
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        """Get price history for a product"""
        with APITimer('GET', f'/api/products/{pk}/price_history/'):
            try:
                product = self.get_object()
                history = PriceHistory.objects.filter(product=product).order_by('-timestamp')[:50]
                serializer = PriceHistorySerializer(history, many=True)
                
                return Response({
                    'success': True,
                    'history': serializer.data
                })
                
            except Exception as e:
                logger.error(f"Error getting price history: {str(e)}")
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompetitorViewSet(viewsets.ModelViewSet):
    """ViewSet for Competitor CRUD operations"""
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def trigger_scrape(self, request, pk=None):
        """Trigger scraping for a specific competitor"""
        with APITimer('POST', f'/api/competitors/{pk}/trigger_scrape/'):
            try:
                competitor = self.get_object()
                
                # Import here to avoid circular imports
                from scraper.tasks import scrape_competitor_prices
                
                # Start scraping task
                task = scrape_competitor_prices.delay(competitor_id=str(competitor.id))
                
                return Response({
                    'success': True,
                    'task_id': task.id,
                    'message': 'Scraping task started'
                })
                
            except Exception as e:
                logger.error(f"Error triggering scrape: {str(e)}")
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PricingRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for PricingRule CRUD operations"""
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def test_rule(self, request, pk=None):
        """Test a pricing rule against products"""
        with APITimer('POST', f'/api/pricing-rules/{pk}/test_rule/'):
            try:
                rule = self.get_object()
                product_ids = request.data.get('product_ids', [])
                
                if not product_ids:
                    return Response({
                        'success': False,
                        'error': 'product_ids is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                products = Product.objects.filter(id__in=product_ids)
                pricing_engine = PricingEngine()
                
                results = []
                for product in products:
                    recommendation = pricing_engine.recommend_price(product, [rule])
                    results.append({
                        'product_id': str(product.id),
                        'product_name': product.name,
                        'current_price': float(product.current_price),
                        'recommended_price': float(recommendation['recommended_price']),
                        'confidence': recommendation['confidence'],
                        'reasoning': recommendation['reasoning']
                    })
                
                return Response({
                    'success': True,
                    'results': results
                })
                
            except Exception as e:
                logger.error(f"Error testing rule: {str(e)}")
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PricingDecisionViewSet(viewsets.ModelViewSet):
    """ViewSet for PricingDecision operations"""
    queryset = PricingDecision.objects.all()
    serializer_class = PricingDecisionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a pending pricing decision"""
        with APITimer('POST', f'/api/pricing-decisions/{pk}/approve/'):
            try:
                decision = self.get_object()
                
                if decision.status != 'pending':
                    return Response({
                        'success': False,
                        'error': 'Decision is not in pending status'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update product price
                old_price = float(decision.product.current_price)
                decision.product.current_price = decision.new_price
                decision.product.save()
                
                # Update decision
                decision.status = 'applied'
                decision.approved_by = request.user
                decision.save()
                
                # Record metrics
                MetricsCollector.record_pricing_decision(decision.decision_source, 'applied')
                MetricsCollector.record_price_change(
                    decision.product.category, 
                    old_price, 
                    float(decision.new_price)
                )
                
                return Response({
                    'success': True,
                    'message': 'Decision approved and applied'
                })
                
            except Exception as e:
                logger.error(f"Error approving decision: {str(e)}")
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pending pricing decision"""
        with APITimer('POST', f'/api/pricing-decisions/{pk}/reject/'):
            try:
                decision = self.get_object()
                
                if decision.status != 'pending':
                    return Response({
                        'success': False,
                        'error': 'Decision is not in pending status'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                decision.status = 'rejected'
                decision.approved_by = request.user
                decision.save()
                
                # Record metrics
                MetricsCollector.record_pricing_decision(decision.decision_source, 'rejected')
                
                return Response({
                    'success': True,
                    'message': 'Decision rejected'
                })
                
            except Exception as e:
                logger.error(f"Error rejecting decision: {str(e)}")
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@action(detail=False, methods=['post'])
def bulk_price_optimization(request):
    """Run bulk price optimization"""
    with APITimer('POST', '/api/bulk-price-optimization/'):
        try:
            product_ids = request.data.get('product_ids')
            auto_apply = request.data.get('auto_apply', False)
            
            pricing_engine = PricingEngine()
            result = pricing_engine.bulk_price_optimization(product_ids)
            
            # Auto-apply if requested
            if auto_apply:
                pending_decisions = PricingDecision.objects.filter(
                    status='pending',
                    product__id__in=product_ids if product_ids else []
                )
                
                applied_count = 0
                for decision in pending_decisions:
                    try:
                        old_price = float(decision.product.current_price)
                        decision.product.current_price = decision.new_price
                        decision.product.save()
                        
                        decision.status = 'applied'
                        decision.approved_by = request.user
                        decision.save()
                        
                        # Record metrics
                        MetricsCollector.record_pricing_decision(decision.decision_source, 'applied')
                        MetricsCollector.record_price_change(
                            decision.product.category, 
                            old_price, 
                            float(decision.new_price)
                        )
                        
                        applied_count += 1
                    except Exception as e:
                        logger.error(f"Error applying decision {decision.id}: {str(e)}")
                
                result['decisions_applied'] = applied_count
            
            return Response({
                'success': True,
                'result': result
            })
            
        except Exception as e:
            logger.error(f"Error in bulk optimization: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
