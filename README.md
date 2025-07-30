# OmniPriceX - Microservices Architecture

AI-powered dynamic pricing system built with microservices architecture using FastAPI, MongoDB Atlas, and gRPC.

## Architecture Overview

```
┌─────────────────┐    REST API    ┌─────────────────┐
│   React Frontend│◄──────────────►│   API Gateway   │
└─────────────────┘                │  (FastAPI)      │
                                   └─────────┬───────┘
                                            │ gRPC
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
           ┌────────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
           │  Product Service│    │ Pricing Service │    │ Scraper Service │
           │   (FastAPI)     │    │   (FastAPI)     │    │   (FastAPI)     │
           └─────────────────┘    └─────────────────┘    └─────────────────┘
                    │                       │                       │
           ┌────────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
           │ Competitor Svc  │    │ Analytics Svc   │    │ LLM Assistant   │
           │   (FastAPI)     │    │   (FastAPI)     │    │   (FastAPI)     │
           └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Services

### Core Services
- **API Gateway** (Port 8000) - REST API for frontend
- **Product Service** (Port 8001) - Product management
- **Pricing Service** (Port 8002) - Pricing engine & rules
- **Scraper Service** (Port 8003) - Competitor data scraping
- **Competitor Service** (Port 8004) - Competitor management
- **Analytics Service** (Port 8005) - Data analytics & reporting
- **LLM Assistant Service** (Port 8006) - AI-powered pricing suggestions

### Infrastructure Services
- **MongoDB Atlas** - Shared database
- **Redis** - Caching & message queuing
- **RabbitMQ** - Task queue for Celery
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards

## Communication
- **Frontend ↔ API Gateway**: REST/HTTP
- **API Gateway ↔ Services**: gRPC
- **Service ↔ Service**: gRPC
- **Async Tasks**: Celery + RabbitMQ

## Development Setup

```bash
# Start all services
docker-compose up -d

# Or run individual services
cd services/api-gateway && python main.py
cd services/product-service && python main.py
cd services/pricing-service && python main.py
# ... etc
```

## Service Discovery
Services register with a discovery mechanism and communicate via gRPC using service names.

## Data Flow
1. Frontend sends REST requests to API Gateway
2. API Gateway routes to appropriate microservice via gRPC
3. Services communicate with each other via gRPC as needed
4. Async tasks (scraping, pricing) handled via Celery
5. All services share MongoDB Atlas database

## Features
- Dynamic pricing adjustments based on real-time data.
- Scalable architecture to handle varying loads.
- Machine learning algorithms for price optimization.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.