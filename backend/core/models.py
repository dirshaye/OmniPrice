from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Competitor(models.Model):
    """Model to store competitor information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    domain = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Scraping configuration
    scraping_enabled = models.BooleanField(default=True)
    scraping_frequency = models.IntegerField(default=3600, help_text="Scraping frequency in seconds")
    last_scraped = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Enhanced Product model for dynamic pricing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    
    # Pricing information
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Inventory
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Competitor tracking
    competitors = models.ManyToManyField(Competitor, through='CompetitorProduct', blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price and self.current_price:
            return ((self.current_price - self.cost_price) / self.current_price) * 100
        return None
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        return self.stock_quantity <= self.low_stock_threshold

class CompetitorProduct(models.Model):
    """Junction table for Product-Competitor relationship with additional data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    competitor_sku = models.CharField(max_length=100, blank=True)
    competitor_url = models.URLField()
    
    # Price tracking
    current_competitor_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_in_stock = models.BooleanField(default=True)
    last_checked = models.DateTimeField(auto_now=True)
    
    # Scraping metadata
    scraping_enabled = models.BooleanField(default=True)
    scraping_errors = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['product', 'competitor']
        ordering = ['competitor__name']
    
    def __str__(self):
        return f"{self.product.name} @ {self.competitor.name}"

class PriceHistory(models.Model):
    """Track price changes over time"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    competitor_product = models.ForeignKey(
        CompetitorProduct, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='price_history'
    )
    
    # Price data
    our_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    competitor_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Context
    timestamp = models.DateTimeField(auto_now_add=True)
    price_change_reason = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manual Update'),
            ('auto_rule', 'Automatic Rule'),
            ('ml_model', 'ML Model Recommendation'),
            ('competitor_change', 'Competitor Price Change'),
            ('inventory_change', 'Inventory Level Change'),
            ('seasonal', 'Seasonal Adjustment'),
        ],
        default='manual'
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['product', '-timestamp']),
            models.Index(fields=['competitor_product', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class PricingRule(models.Model):
    """Define pricing rules and strategies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Rule configuration
    rule_type = models.CharField(
        max_length=20,
        choices=[
            ('undercut', 'Undercut Competitor'),
            ('margin_target', 'Target Margin'),
            ('stock_based', 'Stock Level Based'),
            ('seasonal', 'Seasonal Adjustment'),
            ('custom', 'Custom Logic'),
        ]
    )
    
    # Target products
    products = models.ManyToManyField(Product, blank=True)
    categories = models.JSONField(default=list, blank=True)
    
    # Rule parameters
    parameters = models.JSONField(default=dict, help_text="Rule-specific parameters")
    
    # Control
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher number = higher priority")
    
    # Scheduling
    schedule_enabled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True, help_text="Cron expression for scheduling")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.rule_type})"

class PricingDecision(models.Model):
    """Log all pricing decisions made by the system"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pricing_decisions')
    
    # Decision details
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    decision_source = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual'),
            ('rule_engine', 'Rule Engine'),
            ('ml_model', 'ML Model'),
            ('api', 'API Call'),
        ]
    )
    
    # Context
    applied_rule = models.ForeignKey(PricingRule, on_delete=models.SET_NULL, null=True, blank=True)
    confidence_score = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence score for ML-based decisions"
    )
    reasoning = models.TextField(blank=True, help_text="Explanation for the price change")
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('applied', 'Applied'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['product', '-timestamp']),
            models.Index(fields=['status', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.product.name}: ${self.old_price} → ${self.new_price}"
