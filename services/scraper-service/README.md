# OmniPriceX Scraper Service 🕷️

High-performance web scraping service using **Playwright** for competitive price monitoring.

## Features ✨

- **🎭 Playwright Integration**: Modern browser automation with anti-detection
- **⚡ Async Processing**: Celery-based task queue for scalable scraping
- **🔄 gRPC API**: Fast inter-service communication
- **📊 MongoDB Storage**: Persistent job tracking and results
- **🛡️ Anti-Detection**: Rotating user agents, realistic delays
- **🎯 Smart Extraction**: Intelligent product data parsing
- **📈 Monitoring**: Built-in health checks and metrics

## Quick Start 🚀

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
./setup_playwright.sh
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

### 3. Start Services

```bash
# Terminal 1: Start Redis (for Celery)
redis-server

# Terminal 2: Start Celery Worker
python worker.py

# Terminal 3: Start gRPC Service
python main.py
```

### 4. Test Scraper

```bash
# Test basic functionality
python test_scraper.py
```

## Configuration ⚙️

Key environment variables:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=omnipricex

# Task Queue
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Scraping Settings
SCRAPING_DELAY=1.0
MAX_CONCURRENT_SCRAPES=5
SCRAPING_TIMEOUT=30

# Browser Settings
HEADLESS_BROWSER=true
```

## API Usage 📡

### gRPC Service (Port 50004)

```python
# Trigger scraping job
response = client.TriggerScrape(
    scraper_service_pb2.ScrapeRequest(
        url="https://example-store.com/product",
        priority=5
    )
)

# Check job status
status = client.GetScrapeJobStatus(
    scraper_service_pb2.JobStatusRequest(id=job_id)
)

# Get scraping history
for result in client.ListScrapeHistory(
    scraper_service_pb2.HistoryRequest(limit=10)
):
    print(f"Product: {result.title} - ${result.price}")
```

### REST API (Port 8004)

```bash
# Health check
curl http://localhost:8004/health

# Service info
curl http://localhost:8004/
```

## Supported Sites 🌐

The scraper can handle most e-commerce sites including:

- **Amazon** (with anti-bot measures)
- **eBay** 
- **Shopify stores**
- **WooCommerce stores**
- **Custom e-commerce platforms**

### Generic Selectors

The scraper uses intelligent selectors for:
- Product titles (`h1`, `.product-title`, `#productTitle`)
- Prices (`.price`, `[data-testid*="price"]`, `.a-price`)
- Images (`.product-image img`, `.gallery img`)
- Availability (`in stock`, `out of stock`, `add to cart`)

## Data Model 📋

### Scraped Product

```json
{
  "title": "Product Name",
  "price": 29.99,
  "currency": "USD",
  "original_price": 39.99,
  "availability": "in_stock",
  "brand": "Brand Name",
  "description": "Product description...",
  "image_urls": ["https://..."],
  "rating": 4.5,
  "review_count": 123,
  "source_url": "https://...",
  "scraped_at": "2024-01-15T10:30:00Z",
  "raw_data": {...}
}
```

## Architecture 🏗️

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   gRPC Client   │───▶│ Scraper API  │───▶│   MongoDB   │
└─────────────────┘    └──────────────┘    └─────────────┘
                              │
                              ▼
                       ┌──────────────┐    ┌─────────────┐
                       │ Celery Queue │───▶│ Playwright  │
                       └──────────────┘    └─────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │    Redis     │
                       └──────────────┘
```

## Anti-Detection Features 🛡️

- **Rotating User Agents**: Mimics real browsers
- **Realistic Delays**: Human-like browsing patterns
- **Viewport Randomization**: Different screen sizes
- **JavaScript Support**: Full browser rendering
- **Cookie Management**: Session persistence
- **Proxy Support**: IP rotation (configurable)

## Monitoring 📊

### Health Checks

```bash
# Service health
curl http://localhost:8004/health

# gRPC health check
grpcurl -plaintext localhost:50004 grpc.health.v1.Health/Check
```

### Metrics

- Scraping success/failure rates
- Average response times
- Queue lengths
- Browser resource usage

## Development 🔧

### Project Structure

```
scraper-service/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── models.py          # Database models
│   ├── database.py        # DB connection
│   ├── service.py         # gRPC service
│   ├── tasks.py           # Celery tasks
│   ├── playwright_scraper.py  # Core scraper
│   └── proto/             # gRPC definitions
├── main.py                # Service entry point
├── worker.py              # Celery worker
├── test_scraper.py        # Testing script
└── requirements.txt       # Dependencies
```

### Testing

```bash
# Unit tests
python -m pytest tests/

# Integration test
python test_scraper.py

# Load testing
python test_load.py
```

### Adding New Sites

1. Add site-specific selectors to `playwright_scraper.py`
2. Create custom extraction logic if needed
3. Add test cases in `test_scraper.py`

## Deployment 🚀

### Docker

```bash
# Build image
docker build -t omnipricex/scraper-service .

# Run with Docker Compose
docker-compose up scraper-service
```

### Production Settings

```env
# Performance
MAX_CONCURRENT_SCRAPES=10
SCRAPING_DELAY=2.0
HEADLESS_BROWSER=true

# Scaling
CELERY_WORKERS=4
CELERY_CONCURRENCY=8

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

## Troubleshooting 🔧

### Common Issues

1. **Browser Installation**: Run `./setup_playwright.sh`
2. **Permission Errors**: Check file permissions and Docker setup
3. **Memory Issues**: Reduce concurrent scrapes or add more RAM
4. **Rate Limiting**: Increase delays between requests

### Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with visible browser
export HEADLESS_BROWSER=false

# Check Celery status
celery -A app.tasks inspect active
```

## Contributing 🤝

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License 📄

MIT License - see LICENSE file for details.

---

**OmniPriceX Scraper Service** - Powering competitive intelligence with modern web scraping 🚀
