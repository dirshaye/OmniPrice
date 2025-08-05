# Pricing Service

AI-powered pricing engine with rule-based pricing strategies, competitor analysis, and dynamic price recommendations.

## Features

### 🎯 Core Pricing Engine
- **Multiple Pricing Strategies**: Competitor-based, margin-based, demand-based, cost-plus, dynamic, and promotional pricing
- **Intelligent Rule System**: Priority-based rule execution with confidence scoring
- **Price Validation**: Automatic bounds checking and change limits
- **Impact Estimation**: Revenue and demand impact predictions

### 📊 Pricing Rules Management
- **Flexible Rule Definition**: Support for product IDs, categories, brands, and tags
- **Scheduled Execution**: Cron-based rule scheduling with timezone support
- **Rule Analytics**: Execution statistics and success tracking
- **Priority System**: Weighted rule application based on priority levels

### 🔍 Price Analysis & History
- **Competitor Tracking**: Multi-competitor price monitoring and analysis
- **Historical Analysis**: Price change tracking with market context
- **Trend Detection**: Price pattern recognition and market insights
- **Decision Audit Trail**: Complete history of pricing decisions

### ⚡ Pricing Decisions Workflow
- **Automated Recommendations**: ML-powered price suggestions
- **Approval Workflow**: Manual review and approval process
- **Bulk Operations**: Mass price updates with confidence filtering
- **Real-time Monitoring**: Live pricing decision tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Pricing Service                          │
├─────────────────────────────────────────────────────────────┤
│  gRPC API (Port 50052)                                     │
│  ├── RecommendPrice          ├── CreatePricingRule         │
│  ├── BulkRecommendPrices     ├── ExecutePricingRule        │
│  ├── GetPriceHistory         ├── ListPricingDecisions      │
│  └── RecordPriceChange       └── ApprovePricingDecision    │
├─────────────────────────────────────────────────────────────┤
│  Pricing Engine                                            │
│  ├── Competitor-Based Rules  ├── Dynamic Algorithms        │
│  ├── Margin-Based Rules      ├── Impact Estimation         │
│  ├── Demand-Based Rules      ├── Price Validation          │
│  └── Cost-Plus Rules         └── Confidence Scoring        │
├─────────────────────────────────────────────────────────────┤
│  Database Models (MongoDB)                                 │
│  ├── PricingRule            ├── PriceHistory               │
│  ├── PricingDecision        └── Indexes & Analytics        │
│  └── RecommendationModel                                   │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies
```bash
cd services/pricing-service
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
# .env file
MONGO_URI=mongodb://localhost:27017
MONGO_DB=pricing_service_db
GRPC_PORT=50052
LOG_LEVEL=INFO

# Business Rules
DEFAULT_CONFIDENCE_THRESHOLD=0.7
MAX_PRICE_CHANGE_PERCENTAGE=20.0
COMPETITOR_PRICE_WEIGHT=0.4
MARKET_DEMAND_WEIGHT=0.3
COST_MARGIN_WEIGHT=0.3
```

### 3. Start MongoDB
```bash
docker run -d -p 27017:27017 --name pricing-mongodb mongo:7.0
```

### 4. Run Service
```bash
python main.py
```

### 5. Test Service
```bash
python test_client.py
python status_check.py
```

## API Methods

### Price Recommendations
- **RecommendPrice**: Generate single product price recommendation
- **BulkRecommendPrices**: Bulk price recommendations with filtering

### Pricing Rules
- **CreatePricingRule**: Create new pricing rule
- **GetPricingRule**: Retrieve specific rule
- **UpdatePricingRule**: Modify existing rule
- **DeletePricingRule**: Remove rule
- **ListPricingRules**: Paginated rule listing
- **ExecutePricingRule**: Execute rule on products

### Pricing Decisions
- **CreatePricingDecision**: Create pricing decision
- **ApprovePricingDecision**: Approve decision
- **RejectPricingDecision**: Reject decision
- **ListPricingDecisions**: List decisions with filters

### Price History
- **GetPriceHistory**: Retrieve historical pricing data
- **RecordPriceChange**: Record price change event

## Pricing Strategies

### 1. Competitor-Based Pricing
```python
# Match average competitor price with margin
{
  "strategy": "match_average",
  "margin": 5.0  # 5% margin above average
}

# Undercut minimum competitor price
{
  "strategy": "undercut",
  "undercut_percentage": 3.0  # 3% below minimum
}

# Premium pricing above maximum
{
  "strategy": "premium", 
  "premium_percentage": 10.0  # 10% above maximum
}
```

### 2. Margin-Based Pricing
```python
{
  "target_margin_percentage": 25.0,
  "cost_price": 75.00
}
```

### 3. Dynamic Pricing
```python
{
  "competitor_weight": 0.4,
  "demand_weight": 0.3,
  "cost_weight": 0.3
}
```

### 4. Promotional Pricing
```python
{
  "discount_percentage": 15.0,
  "min_price": 50.00
}
```

## Configuration

### Business Rules
```python
# Maximum allowed price change
MAX_PRICE_CHANGE_PERCENTAGE = 20.0

# Minimum price threshold  
MIN_PRICE_THRESHOLD = 0.01

# Default confidence threshold
DEFAULT_CONFIDENCE_THRESHOLD = 0.7

# Algorithm weights
COMPETITOR_PRICE_WEIGHT = 0.4
MARKET_DEMAND_WEIGHT = 0.3
COST_MARGIN_WEIGHT = 0.3
```

### Database Models

#### PricingRule
- Rule definition with conditions and parameters
- Priority-based execution order
- Scheduling support with cron expressions
- Performance analytics

#### PricingDecision  
- Price change recommendations
- Approval workflow status
- Impact analysis data
- Audit trail information

#### PriceHistory
- Historical price tracking
- Competitor price monitoring
- Market condition context
- Change reason tracking

## Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Integration Tests
```bash
python test_client.py
```

### Performance Tests
```bash
python -m pytest tests/performance/
```

## Monitoring

### Health Check
```bash
python status_check.py
```

### Metrics
- Rule execution success rate
- Average confidence scores
- Price change distribution
- Decision approval rates

### Logging
```python
# Structured logging with correlation IDs
logger.info("🎯 Price recommendation", extra={
    "product_id": "PROD_001",
    "confidence": 0.85,
    "price_change": 5.99
})
```

## Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Environment Variables
```bash
MONGO_URI=mongodb://mongodb:27017
GRPC_PORT=50052
LOG_LEVEL=INFO
DEFAULT_CONFIDENCE_THRESHOLD=0.8
MAX_PRICE_CHANGE_PERCENTAGE=15.0
```

### Scaling Considerations
- MongoDB sharding for large datasets
- Read replicas for query performance
- Rate limiting for API protection
- Circuit breakers for external dependencies

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check MongoDB connectivity
   - Verify credentials and network access
   - Review connection string format

2. **Rule Execution Failures**
   - Validate rule parameters
   - Check product data availability
   - Review confidence thresholds

3. **Performance Issues**
   - Monitor database indexes
   - Optimize rule complexity
   - Consider caching strategies

4. **Price Validation Errors**
   - Review price bounds configuration
   - Check minimum price thresholds
   - Validate change percentage limits

### Debug Mode
```bash
LOG_LEVEL=DEBUG python main.py
```

### Health Monitoring
```bash
# Service status
curl -s localhost:50052/health

# Database status  
python -c "from app.database import *; print('DB OK')"

# Rule performance
python scripts/analyze_rules.py
```

## Development

### Adding New Pricing Strategies
1. Extend `RuleType` enum
2. Implement strategy in `PricingEngine`
3. Add parameter validation
4. Create unit tests
5. Update documentation

### Custom Business Rules
1. Define rule parameters schema
2. Implement validation logic
3. Add execution metrics
4. Test edge cases
5. Document configuration

## License

Part of OmniPriceX - AI-Powered Dynamic Pricing Platform
