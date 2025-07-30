from rest_framework import serializers
from core.models import Product, Competitor, PricingRule, PricingDecision, PriceHistory, CompetitorProduct

class CompetitorSerializer(serializers.ModelSerializer):
    """Serializer for Competitor model"""
    
    class Meta:
        model = Competitor
        fields = [
            'id', 'name', 'domain', 'is_active', 'created_at', 'updated_at',
            'scraping_enabled', 'scraping_frequency', 'last_scraped'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_scraped']

class CompetitorProductSerializer(serializers.ModelSerializer):
    """Serializer for CompetitorProduct model"""
    competitor_name = serializers.CharField(source='competitor.name', read_only=True)
    
    class Meta:
        model = CompetitorProduct
        fields = [
            'id', 'competitor', 'competitor_name', 'competitor_sku', 
            'competitor_url', 'current_competitor_price', 'is_in_stock',
            'last_checked', 'scraping_enabled', 'scraping_errors', 'last_error'
        ]
        read_only_fields = ['id', 'last_checked', 'scraping_errors', 'last_error']

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    profit_margin = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    competitor_products = CompetitorProductSerializer(
        source='competitorproduct_set', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'category', 'brand',
            'base_price', 'current_price', 'min_price', 'max_price', 'cost_price',
            'stock_quantity', 'low_stock_threshold', 'is_active',
            'created_at', 'updated_at', 'created_by',
            'profit_margin', 'is_low_stock', 'competitor_products'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'profit_margin', 
            'is_low_stock', 'competitor_products'
        ]
    
    def create(self, validated_data):
        """Set created_by to current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class PricingRuleSerializer(serializers.ModelSerializer):
    """Serializer for PricingRule model"""
    
    class Meta:
        model = PricingRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'products', 'categories',
            'parameters', 'is_active', 'priority', 'schedule_enabled', 
            'schedule_cron', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Set created_by to current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class PricingDecisionSerializer(serializers.ModelSerializer):
    """Serializer for PricingDecision model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    applied_rule_name = serializers.CharField(source='applied_rule.name', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    price_change_amount = serializers.SerializerMethodField()
    price_change_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = PricingDecision
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'old_price', 'new_price', 'price_change_amount', 'price_change_percentage',
            'decision_source', 'applied_rule', 'applied_rule_name',
            'confidence_score', 'reasoning', 'status',
            'timestamp', 'approved_by', 'approved_by_username'
        ]
        read_only_fields = [
            'id', 'timestamp', 'product_name', 'product_sku', 
            'applied_rule_name', 'approved_by_username',
            'price_change_amount', 'price_change_percentage'
        ]
    
    def get_price_change_amount(self, obj):
        """Calculate price change amount"""
        return float(obj.new_price - obj.old_price)
    
    def get_price_change_percentage(self, obj):
        """Calculate price change percentage"""
        if obj.old_price == 0:
            return 0
        return float((obj.new_price - obj.old_price) / obj.old_price * 100)

class PriceHistorySerializer(serializers.ModelSerializer):
    """Serializer for PriceHistory model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    competitor_name = serializers.CharField(
        source='competitor_product.competitor.name', 
        read_only=True
    )
    
    class Meta:
        model = PriceHistory
        fields = [
            'id', 'product', 'product_name', 'competitor_product', 'competitor_name',
            'our_price', 'competitor_price', 'timestamp', 'price_change_reason'
        ]
        read_only_fields = ['id', 'timestamp', 'product_name', 'competitor_name']

class ProductSummarySerializer(serializers.ModelSerializer):
    """Simplified Product serializer for lists"""
    competitor_count = serializers.SerializerMethodField()
    latest_decision = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'current_price', 
            'stock_quantity', 'is_active', 'competitor_count', 'latest_decision'
        ]
    
    def get_competitor_count(self, obj):
        """Get number of competitors tracking this product"""
        return obj.competitorproduct_set.filter(competitor__is_active=True).count()
    
    def get_latest_decision(self, obj):
        """Get latest pricing decision"""
        latest = obj.pricing_decisions.first()
        if latest:
            return {
                'id': str(latest.id),
                'new_price': float(latest.new_price),
                'status': latest.status,
                'timestamp': latest.timestamp
            }
        return None

class BulkPriceUpdateSerializer(serializers.Serializer):
    """Serializer for bulk price updates"""
    product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="List of product IDs to update. If not provided, all products will be processed."
    )
    auto_apply = serializers.BooleanField(
        default=False,
        help_text="Whether to automatically apply pricing recommendations"
    )
    rule_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Specific rules to apply. If not provided, all applicable rules will be used."
    )

class PriceRecommendationSerializer(serializers.Serializer):
    """Serializer for price recommendation requests"""
    product_id = serializers.UUIDField()
    rule_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Specific rules to apply"
    )
    include_competitor_analysis = serializers.BooleanField(default=True)
