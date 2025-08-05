# Product Service

The Product Service is a gRPC-based microservice that manages products, pricing, inventory, and competitor tracking for the OmniPriceX platform.

## 🚀 Features

- **Product Management**: Create, read, update, and delete products
- **Price History Tracking**: Automatic price change history with audit trail
- **Inventory Management**: Stock quantity tracking with low stock alerts
- **Competitor Price Monitoring**: Integration with scraper service for price comparison
- **Bulk Operations**: Efficient bulk product updates
- **Advanced Search**: Text search across product names and descriptions
- **Category Management**: Organize products by categories and brands
- **Status Management**: Track product lifecycle (active, inactive, discontinued, etc.)

## 📋 API Operations

### Core CRUD Operations
- `CreateProduct` - Create a new product
- `GetProduct` - Retrieve a product by ID
- `UpdateProduct` - Update product information
- `DeleteProduct` - Remove a product
- `ListProducts` - List products with pagination and filtering

### Business Operations
- `GetProductsByCategory` - Get products filtered by category
- `GetLowStockProducts` - Find products with low inventory
- `UpdateProductPrice` - Update price with history tracking
- `BulkUpdateProducts` - Update multiple products at once

## 🏗️ Architecture

```
Product Service
├── main.py              # gRPC server entry point
├── app/
│   ├── service.py       # gRPC service implementation
│   ├── database.py      # Database connection and models
│   ├── config.py        # Configuration management
│   └── scraper_integration.py  # Scraper service integration
├── Dockerfile           # Container configuration
├── requirements.txt     # Python dependencies
└── .env                # Environment configuration
```

## 🛠️ Technology Stack

- **gRPC**: High-performance RPC framework
- **Python 3.11**: Runtime environment
- **Beanie**: Async ODM for MongoDB
- **MongoDB**: Document database for product storage
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and settings management

## 📊 Data Model

### Product
```python
{
    "id": "ObjectId",
    "name": "Product Name",
    "sku": "UNIQUE-SKU",
    "description": "Product description",
    "category": "Electronics",
    "brand": "BrandName",
    "base_price": 99.99,
    "current_price": 89.99,
    "min_price": 50.0,
    "max_price": 150.0,
    "cost_price": 40.0,
    "stock_quantity": 100,
    "low_stock_threshold": 10,
    "status": "active|inactive|discontinued|out_of_stock|pending",
    "is_active": true,
    "competitor_urls": {
        "competitor1": "https://example.com/product"
    },
    "tags": ["electronics", "gadgets"],
    "price_history": [...],
    "competitor_data": [...],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "user_id"
}
```

### Price History
```python
{
    "price": 89.99,
    "currency": "USD",
    "changed_at": "2024-01-01T00:00:00Z",
    "changed_by": "user_id",
    "reason": "Promotional discount"
}
```

### Competitor Data
```python
{
    "competitor_name": "Competitor Store",
    "url": "https://competitor.com/product",
    "price": 95.99,
    "currency": "USD",
    "last_scraped": "2024-01-01T00:00:00Z",
    "is_available": true,
    "scrape_errors": []
}
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB instance
- Access to shared proto files

### Development Setup

1. **Clone and navigate to the service directory**:
   ```bash
   cd services/product-service
   ```

2. **Run the development setup script**:
   ```bash
   ./start_dev.sh
   ```

   This script will:
   - Create a virtual environment
   - Install dependencies
   - Check database connectivity
   - Generate proto files if needed
   - Start the service

3. **Manual setup (alternative)**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start the service
   python main.py
   ```

### Configuration

Create a `.env` file with your configuration:

```env
# Service Configuration
SERVICE_NAME=product-service
SERVICE_VERSION=1.0.0
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8003
GRPC_PORT=50053

# Database
MONGO_URI=mongodb://localhost:27017
MONGO_DB=omnipricex

# Business Rules
DEFAULT_CURRENCY=USD
DEFAULT_LOW_STOCK_THRESHOLD=10
MAX_COMPETITORS_PER_PRODUCT=20
PRICE_HISTORY_LIMIT=100

# Logging
LOG_LEVEL=INFO
```

## 🧪 Testing

### Run the Test Client

```bash
python test_client_new.py
```

The test client will:
- Create sample products
- Test all CRUD operations
- Verify price history tracking
- Test bulk operations
- Clean up test data

### Test with gRPC Client

```python
import grpc
from shared.proto import product_service_pb2
from shared.proto import product_service_pb2_grpc

# Connect to service
channel = grpc.insecure_channel('localhost:50053')
stub = product_service_pb2_grpc.ProductServiceStub(channel)

# Create a product
request = product_service_pb2.CreateProductRequest(
    name="Test Product",
    sku="TEST-001",
    category="Electronics",
    base_price=99.99,
    current_price=89.99,
    stock_quantity=100,
    created_by="test_user"
)

response = stub.CreateProduct(request)
print(f"Product created: {response.success}")
```

## 🐳 Docker Deployment

### Build the Docker Image

```bash
docker build -t omnipricex/product-service .
```

### Run with Docker

```bash
docker run -d \
  --name product-service \
  -p 50053:50053 \
  -e MONGO_URI="mongodb://your-mongo-uri" \
  -e MONGO_DB="omnipricex" \
  omnipricex/product-service
```

### Docker Compose

```yaml
version: '3.8'
services:
  product-service:
    build: .
    ports:
      - "50053:50053"
    environment:
      - MONGO_URI=mongodb://mongodb:27017
      - MONGO_DB=omnipricex
    depends_on:
      - mongodb
```

## 🔧 Integration

### With Scraper Service

The Product Service integrates with the Scraper Service for competitor price monitoring:

```python
from app.scraper_integration import scrape_product_competitors

# Scrape competitor prices for a product
prices = await scrape_product_competitors(product)
```

### With Other Services

The service uses shared proto definitions from `/shared/proto/` for consistency across the platform.

## 📈 Monitoring and Health Checks

### Health Check Endpoint

The service includes basic health monitoring. Check if the service is running:

```bash
# Test gRPC connection
grpc_health_probe -addr=localhost:50053
```

### Logs

The service provides structured logging with different levels:

```bash
# View logs (if running with Docker)
docker logs product-service -f
```

## 🔒 Security Considerations

- **Input Validation**: All inputs are validated using Pydantic models
- **Error Handling**: Comprehensive error handling with appropriate gRPC status codes
- **Data Sanitization**: Automatic data cleaning and validation
- **Access Control**: Ready for authentication integration

## 📝 API Documentation

### gRPC Service Definition

The service is defined in `/shared/proto/product_service.proto` with the following methods:

```protobuf
service ProductService {
    rpc CreateProduct(CreateProductRequest) returns (ProductResponse);
    rpc GetProduct(GetProductRequest) returns (ProductResponse);
    rpc UpdateProduct(UpdateProductRequest) returns (ProductResponse);
    rpc DeleteProduct(DeleteProductRequest) returns (google.protobuf.Empty);
    rpc ListProducts(ListProductsRequest) returns (ListProductsResponse);
    rpc GetProductsByCategory(GetProductsByCategoryRequest) returns (ListProductsResponse);
    rpc GetLowStockProducts(google.protobuf.Empty) returns (ListProductsResponse);
    rpc UpdateProductPrice(UpdateProductPriceRequest) returns (ProductResponse);
    rpc BulkUpdateProducts(BulkUpdateProductsRequest) returns (BulkUpdateProductsResponse);
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MongoDB URI in `.env`
   - Ensure MongoDB is running
   - Verify network connectivity

2. **Proto Files Not Found**
   - Run the `start_dev.sh` script to generate proto files
   - Ensure shared directory structure is correct

3. **Import Errors**
   - Check Python path includes shared directory
   - Verify all dependencies are installed

4. **Port Already in Use**
   - Change `GRPC_PORT` in configuration
   - Check for other services using port 50053

### Debug Mode

Enable debug mode for detailed logging:

```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure all tests pass before submitting

## 📄 License

This service is part of the OmniPriceX platform and follows the project's licensing terms.

---

For more information about the OmniPriceX platform, see the main project documentation.
