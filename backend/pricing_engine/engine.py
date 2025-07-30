from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import logging
from django.utils import timezone
from django.db.models import Avg, Min, Max, Q

from core.models import Product, PricingRule, PricingDecision, CompetitorProduct, PriceHistory

logger = logging.getLogger(__name__)

class PricingEngine:
    """
    Main pricing engine that applies rules and ML models to determine optimal prices
    """
    
    def __init__(self):
        self.rule_processors = {
            'undercut': self._process_undercut_rule,
            'margin_target': self._process_margin_target_rule,
            'stock_based': self._process_stock_based_rule,
            'seasonal': self._process_seasonal_rule,
            'custom': self._process_custom_rule,
        }
    
    def recommend_price(self, product: Product, rules: Optional[List[PricingRule]] = None) -> Dict:
        """
        Generate price recommendation for a product
        
        Returns:
            dict: {
                'recommended_price': Decimal,
                'confidence': float,
                'reasoning': str,
                'applied_rules': List[str],
                'competitor_analysis': Dict
            }
        """
        try:
            # Get applicable rules
            if not rules:
                rules = self._get_applicable_rules(product)
            
            # Analyze competitor prices
            competitor_analysis = self._analyze_competitor_prices(product)
            
            # Apply rules in priority order
            recommendations = []
            applied_rules = []
            
            for rule in rules:
                try:
                    result = self._apply_rule(product, rule, competitor_analysis)
                    if result:
                        recommendations.append(result)
                        applied_rules.append(rule.name)
                        logger.info(f"Applied rule '{rule.name}' to {product.name}: ${result['price']}")
                except Exception as e:
                    logger.error(f"Error applying rule '{rule.name}' to {product.name}: {str(e)}")
            
            # Combine recommendations
            final_recommendation = self._combine_recommendations(
                product, recommendations, competitor_analysis
            )
            
            # Add metadata
            final_recommendation.update({
                'applied_rules': applied_rules,
                'competitor_analysis': competitor_analysis,
                'timestamp': timezone.now()
            })
            
            return final_recommendation
            
        except Exception as e:
            logger.error(f"Error generating price recommendation for {product.name}: {str(e)}")
            return {
                'recommended_price': product.current_price,
                'confidence': 0.0,
                'reasoning': f"Error in pricing engine: {str(e)}",
                'applied_rules': [],
                'competitor_analysis': {}
            }
    
    def _get_applicable_rules(self, product: Product) -> List[PricingRule]:
        """Get applicable pricing rules for a product"""
        rules = PricingRule.objects.filter(
            Q(products=product) | 
            Q(categories__contains=product.category) |
            Q(products__isnull=True, categories=[]),
            is_active=True
        ).order_by('-priority', 'name')
        
        return list(rules)
    
    def _analyze_competitor_prices(self, product: Product) -> Dict:
        """Analyze competitor prices for the product"""
        competitor_products = CompetitorProduct.objects.filter(
            product=product,
            current_competitor_price__isnull=False,
            competitor__is_active=True
        )
        
        if not competitor_products.exists():
            return {
                'competitor_count': 0,
                'min_price': None,
                'max_price': None,
                'avg_price': None,
                'our_position': 'unknown'
            }
        
        prices = [cp.current_competitor_price for cp in competitor_products]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        # Determine our position
        our_price = float(product.current_price)
        if our_price < min_price:
            position = 'lowest'
        elif our_price > max_price:
            position = 'highest'
        else:
            position = 'middle'
        
        return {
            'competitor_count': len(prices),
            'min_price': float(min_price),
            'max_price': float(max_price),
            'avg_price': float(avg_price),
            'our_position': position,
            'competitor_prices': [
                {
                    'competitor': cp.competitor.name,
                    'price': float(cp.current_competitor_price),
                    'in_stock': cp.is_in_stock
                }
                for cp in competitor_products
            ]
        }
    
    def _apply_rule(self, product: Product, rule: PricingRule, competitor_analysis: Dict) -> Optional[Dict]:
        """Apply a specific pricing rule"""
        processor = self.rule_processors.get(rule.rule_type)
        if not processor:
            logger.warning(f"No processor found for rule type: {rule.rule_type}")
            return None
        
        return processor(product, rule, competitor_analysis)
    
    def _process_undercut_rule(self, product: Product, rule: PricingRule, competitor_analysis: Dict) -> Dict:
        """Process undercut competitor rule"""
        params = rule.parameters
        undercut_amount = Decimal(str(params.get('undercut_amount', 0.01)))  # Default 1 cent
        undercut_percentage = params.get('undercut_percentage', 0)  # Default 0%
        min_margin = params.get('min_margin_percentage', 0)  # Minimum margin to maintain
        
        if competitor_analysis['competitor_count'] == 0:
            return None
        
        target_price = Decimal(str(competitor_analysis['min_price']))
        
        # Apply undercut
        if undercut_percentage > 0:
            target_price = target_price * (1 - Decimal(str(undercut_percentage / 100)))
        else:
            target_price = target_price - undercut_amount
        
        # Check minimum margin
        if product.cost_price and min_margin > 0:
            min_price = product.cost_price * (1 + Decimal(str(min_margin / 100)))
            if target_price < min_price:
                target_price = min_price
        
        # Respect product price bounds
        target_price = max(target_price, product.min_price)
        target_price = min(target_price, product.max_price)
        
        confidence = 0.8 if competitor_analysis['competitor_count'] >= 3 else 0.6
        
        return {
            'price': target_price,
            'confidence': confidence,
            'reasoning': f"Undercutting lowest competitor price (${competitor_analysis['min_price']})"
        }
    
    def _process_margin_target_rule(self, product: Product, rule: PricingRule, competitor_analysis: Dict) -> Dict:
        """Process target margin rule"""
        params = rule.parameters
        target_margin = params.get('target_margin_percentage', 20)  # Default 20%
        
        if not product.cost_price:
            return None
        
        target_price = product.cost_price * (1 + Decimal(str(target_margin / 100)))
        
        # Respect product price bounds
        target_price = max(target_price, product.min_price)
        target_price = min(target_price, product.max_price)
        
        return {
            'price': target_price,
            'confidence': 0.9,
            'reasoning': f"Target margin of {target_margin}% applied"
        }
    
    def _process_stock_based_rule(self, product: Product, rule: PricingRule, competitor_analysis: Dict) -> Dict:
        """Process stock-based pricing rule"""
        params = rule.parameters
        low_stock_multiplier = Decimal(str(params.get('low_stock_multiplier', 1.1)))  # 10% increase
        high_stock_multiplier = Decimal(str(params.get('high_stock_multiplier', 0.95)))  # 5% decrease
        high_stock_threshold = params.get('high_stock_threshold', 100)
        
        current_price = product.current_price
        
        if product.is_low_stock:
            # Increase price for low stock
            target_price = current_price * low_stock_multiplier
            reasoning = f"Low stock detected, increasing price by {(low_stock_multiplier - 1) * 100:.1f}%"
            confidence = 0.7
        elif product.stock_quantity > high_stock_threshold:
            # Decrease price for high stock
            target_price = current_price * high_stock_multiplier
            reasoning = f"High stock detected, decreasing price by {(1 - high_stock_multiplier) * 100:.1f}%"
            confidence = 0.6
        else:
            return None
        
        # Respect product price bounds
        target_price = max(target_price, product.min_price)
        target_price = min(target_price, product.max_price)
        
        return {
            'price': target_price,
            'confidence': confidence,
            'reasoning': reasoning
        }
    
    def _process_seasonal_rule(self, product: Product, rule: PricingRule, competitor_analysis: Dict) -> Dict:
        """Process seasonal adjustment rule"""
        params = rule.parameters
        seasonal_multiplier = Decimal(str(params.get('seasonal_multiplier', 1.0)))
        
        if seasonal_multiplier == 1.0:
            return None
        
        target_price = product.current_price * seasonal_multiplier
        
        # Respect product price bounds
        target_price = max(target_price, product.min_price)
        target_price = min(target_price, product.max_price)
        
        adjustment = (seasonal_multiplier - 1) * 100
        direction = "increase" if adjustment > 0 else "decrease"
        
        return {
            'price': target_price,
            'confidence': 0.5,
            'reasoning': f"Seasonal {direction} of {abs(adjustment):.1f}% applied"
        }
    
    def _process_custom_rule(self, product: Product, rule: PricingRule, competitor_analysis: Dict) -> Dict:
        """Process custom rule logic"""
        # This would contain custom business logic
        # For now, return None to skip custom rules
        return None
    
    def _combine_recommendations(self, product: Product, recommendations: List[Dict], competitor_analysis: Dict) -> Dict:
        """Combine multiple price recommendations"""
        if not recommendations:
            return {
                'recommended_price': product.current_price,
                'confidence': 0.0,
                'reasoning': "No applicable pricing rules found"
            }
        
        # Weight recommendations by confidence
        weighted_sum = Decimal('0')
        total_weight = Decimal('0')
        reasons = []
        
        for rec in recommendations:
            weight = Decimal(str(rec['confidence']))
            weighted_sum += rec['price'] * weight
            total_weight += weight
            reasons.append(rec['reasoning'])
        
        if total_weight == 0:
            recommended_price = product.current_price
            confidence = 0.0
        else:
            recommended_price = weighted_sum / total_weight
            confidence = float(total_weight / len(recommendations))
        
        # Ensure price is within bounds
        recommended_price = max(recommended_price, product.min_price)
        recommended_price = min(recommended_price, product.max_price)
        
        return {
            'recommended_price': recommended_price,
            'confidence': min(confidence, 1.0),
            'reasoning': '; '.join(reasons)
        }
    
    def apply_price_recommendation(self, product: Product, recommendation: Dict, user=None) -> PricingDecision:
        """Apply a price recommendation and create a pricing decision"""
        decision = PricingDecision.objects.create(
            product=product,
            old_price=product.current_price,
            new_price=recommendation['recommended_price'],
            decision_source='rule_engine',
            confidence_score=recommendation['confidence'],
            reasoning=recommendation['reasoning'],
            status='pending'
        )
        
        return decision
    
    def bulk_price_optimization(self, product_ids: Optional[List] = None) -> Dict:
        """Run pricing optimization for multiple products"""
        if product_ids:
            products = Product.objects.filter(id__in=product_ids, is_active=True)
        else:
            products = Product.objects.filter(is_active=True)
        
        results = {
            'total_products': products.count(),
            'recommendations_generated': 0,
            'decisions_created': 0,
            'errors': []
        }
        
        for product in products:
            try:
                recommendation = self.recommend_price(product)
                results['recommendations_generated'] += 1
                
                # Only create decision if price change is significant
                current_price = float(product.current_price)
                recommended_price = float(recommendation['recommended_price'])
                price_change_pct = abs(recommended_price - current_price) / current_price * 100
                
                if price_change_pct >= 1.0:  # Only if change is >= 1%
                    self.apply_price_recommendation(product, recommendation)
                    results['decisions_created'] += 1
                
            except Exception as e:
                results['errors'].append({
                    'product_id': str(product.id),
                    'error': str(e)
                })
        
        return results
