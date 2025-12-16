# OmniPrice - Dynamic Pricing Platform

AI-powered dynamic pricing system , built with enterprise-grade microservices architecture. Showcases advanced backend engineering, data workflows, and LLM integration for optimal pricing strategies.

> MVP Mode Available: Run as a single FastAPI monolith + React frontend for learning and rapid iteration. See "MVP Monolith Mode" section below.

## 🏗️ Project Structure

```
OmniPrice/
├── README.md                       # Project overview and setup
├── Makefile                        # Build automation and development tasks
├── docker-compose.yml              # Local development environment
├── .github/workflows/              # CI/CD pipelines
├── docs/                           # Comprehensive documentation
│   ├── architecture.md             # System architecture details
│   ├── api/endpoints.md             # API documentation
│   └── deployment/guide.md          # Deployment instructions
├── services/                       # Microservices
│   ├── api-gateway/                # Frontend interface & routing (Port 8000)
│   ├── scraper-service/            # Playwright-based web scraping (Port 8003)
│   ├── external-api-adapter/       # Shopify/Amazon/Google APIs (Port 8005)
│   ├── pricing-service/            # Pricing rules engine (Port 8002)
│   ├── llm-assistant/              # Gemini/GPT-4 pricing AI (Port 8006)
│   ├── scheduler/                  # Prefect 2.x workflows (Port 8007)
│   ├── data-pipeline/              # Pandas/PySpark ETL (Port 8008)
│   ├── product-service/            # Product management (Port 8001)
│   └── auth-service/               # Auth0 integration (Port 8004)
├── frontend/                       # React + Material UI
├── shared/                         # Common libraries & utilities
│   ├── proto/                      # gRPC protocol definitions
│   ├── models/                     # Shared data models
│   ├── config/                     # Common configurations
│   └── utils/                      # Helper utilities
├── infrastructure/                 # Infrastructure as Code
│   └── terraform/                  # AWS resource definitions
├── tests/                          # Test suites
│   ├── integration/                # Service integration tests
│   └── e2e/                        # End-to-end user workflows
├── monitoring/                     # Observability configuration
│   ├── prometheus/                 # Metrics collection
│   └── grafana/                    # Monitoring dashboards
└── scripts/                        # Build and deployment scripts
```

## 🏛️ Architecture Overview

```
┌─────────────────┐    REST API    ┌─────────────────┐
│   React Frontend│◄──────────────►│   API Gateway   │
│   (Port 3000)   │                │  (Port 8000)    │
└─────────────────┘                └─────────┬───────┘
                                            │ gRPC
    ┌──────────────────────────────────────┼──────────────────────────────────────┐
    │                                      │                                      │
┌───▼────┐  ┌──────────┐  ┌──────────┐  ┌─▼────┐  ┌──────────┐  ┌─────────────┐  │
│Products│  │ Pricing  │  │ Scraper  │  │ LLM  │  │Scheduler │  │Data Pipeline│  │
│(8001)  │  │ (8002)   │  │ (8003)   │  │(8006)│  │ (8007)   │  │   (8008)    │  │
└────────┘  └──────────┘  └──────────┘  └──────┘  └──────────┘  └─────────────┘  │
    │                                      │                                      │
    └──────────────────────────────────────┼──────────────────────────────────────┘
                                          │
                ┌─────────────────────────▼─────────────────────────┐
                │              External APIs                        │
                │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
                │  │ Shopify  │  │ Amazon   │  │ Google   │        │
                │  │   API    │  │   API    │  │   API    │        │
                │  └──────────┘  └──────────┘  └──────────┘        │
                └───────────────────────────────────────────────────┘
```

## 🧩 MVP Monolith Mode

This repository now supports a simplified development path: start with a single backend (monolith) before re‑introducing individual microservices, queues, and gRPC. This helps you learn incrementally.

### What's Included in MVP
- FastAPI backend (single process) at http://localhost:8000
- In-memory Products CRUD
- In-memory Pricing Rules + mock recommendation endpoint
- Mock endpoints for competitors, analytics, scraper so the frontend UI doesn’t break
- React frontend at http://localhost:3000

### What's Excluded (for now)
- MongoDB / Redis / RabbitMQ
- Celery tasks & scheduler
- gRPC services
- LLM assistant integration

### Run the MVP
```bash
make mvp-up       # build + start backend + frontend
make mvp-logs     # follow backend logs
make mvp-down     # stop containers
make mvp-reset    # full clean
```

Backend docs: http://localhost:8000/docs

### Migration Roadmap
1. Persist Products to MongoDB
2. Extract Pricing into its own REST service
3. Add Redis + RabbitMQ + Celery for background tasks
4. Split services further (scraper, competitors, analytics)
5. Introduce gRPC between services
6. Add LLM assistant & advanced analytics

Each step can be layered on without rewriting earlier code.

## ⚡ Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- Make

### Development Setup
```bash
# Clone and setup
git clone https://github.com/dirshaye/OmniPrice.git
cd OmniPrice

# Install dependencies
make install

# Generate gRPC code
make generate-proto

# Start development environment
make dev
```

### Access Points
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Prefect UI**: http://localhost:4200

## 🔧 Development Commands

```bash
make install        # Install all dependencies
make test          # Run all tests (Python + Frontend)
make lint          # Run code linting
make format        # Format all code
make build         # Build Docker images
make dev           # Start development environment
make clean         # Clean up containers and images
```

## 🌟 Core Technologies & Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | React + Material UI |
| **API Gateway** | FastAPI (Port 8000) |
| **Scraper Service** | FastAPI + Playwright |
| **External API Adapter** | FastAPI + Shopify/Amazon/Google APIs |
| **Pricing Service** | FastAPI + pricing rules engine |
| **LLM Assistant** | Gemini/GPT-4 via API |
| **Scheduler** | Prefect 2.x |
| **Data Pipeline** | FastAPI + Pandas/PySpark |
| **Database** | MongoDB Atlas |
| **Auth** | Auth0 integration |
| **Message Queue** | Celery + RabbitMQ |
| **Caching** | Redis |
| **Monitoring** | Prometheus + Grafana |

## 🚀 Key Backend Features

### Microservices Architecture
- **FastAPI-based services** communicating via gRPC
- **Independent deployment** with Docker containers
- **Service discovery** and load balancing
- **Circuit breakers** and retry mechanisms

### Async Task Queue
- **Celery + RabbitMQ** for background jobs:
  - Scraping competitor product pages (async scrape jobs)
  - Applying pricing rules immediately after user input
  - Logging results into MongoDB
  - Data cleaning and validation

### Scheduled Workflows (Prefect 2.x)
- **Orchestrated pipelines**:
  - `scrape → clean → analyze → recommend`
  - Monitor competitor prices every X hours
  - Push updates to pricing dashboard and LLM assistant
- **Visual workflow management** with Prefect UI
- **Error handling** and automatic retries

### LLM-Powered Price Assistant
- **Gemini/GPT-4 integration** for:
  - Optimal price recommendations
  - Reasoning explanations using context (inventory, competitors, margin goals, seasonality)
  - Prompt template design with reasoning chains
- **Context-aware recommendations** based on market conditions

### Data Engineering Pipeline
- **Pandas/PySpark** for:
  - Cleaning scraped competitor data
  - Joining historical price trends from MongoDB
  - Analyzing stock levels, competitor patterns, seasonality
- **Real-time and batch processing** capabilities
- **Data quality monitoring** and validation

### Data-as-a-Service API Layer
- **RESTful endpoints** for internal tools:
  - Fetch historical pricing data
  - View current vs recommended prices
  - Manage pricing rules per product/category
- **GraphQL support** for flexible data queries
- **API versioning** and documentation

### Authentication & Authorization
- **Auth0 integration** for secure multi-tenant access
- **JWT-based authentication** with refresh tokens
- **Role-based access control** (RBAC)
- **API key management** for service-to-service communication

## 📊 Advanced Features

### Web Scraping Engine
- **Playwright-based scraping** for JavaScript-heavy sites
- **Anti-detection mechanisms** (rotating proxies, user agents)
- **Concurrent scraping** with rate limiting
- **Error handling** and retry strategies

### External API Integration
- **Shopify API** for e-commerce data
- **Amazon Product Advertising API** for competitor pricing
- **Google Shopping API** for market research
- **Unified adapter pattern** for easy API additions

### Pricing Rules Engine
- **Dynamic rule evaluation** based on:
  - Competitor prices
  - Inventory levels
  - Profit margins
  - Seasonal trends
  - Customer segments
- **A/B testing** for pricing strategies
- **Real-time price updates** via WebSocket

### Monitoring & Observability
- **Prometheus metrics** collection
- **Grafana dashboards** for visualization
- **Distributed tracing** with OpenTelemetry
- **Structured logging** with correlation IDs
- **Health checks** and alerting

## 🔄 Data Flow Architecture

### Real-time Pricing Workflow
1. **User configures pricing rules** → API Gateway
2. **Rules applied immediately** → Pricing Service
3. **Background validation** → LLM Assistant
4. **Price updates pushed** → Frontend via WebSocket

### Competitor Monitoring Workflow
1. **Scheduled scraping** → Prefect triggers Scraper Service
2. **Data cleaning** → Data Pipeline processes raw data
3. **Trend analysis** → Historical comparison and insights
4. **LLM recommendations** → AI-powered pricing suggestions
5. **Dashboard updates** → Real-time notifications to users

### External API Workflow
1. **API calls** → External API Adapter
2. **Data normalization** → Standardized format
3. **Rate limiting** → Respect API quotas
4. **Caching** → Redis for performance
5. **Error handling** → Graceful degradation

## 📈 Showcase Value

This architecture demonstrates:

- **Clean microservices design** with proper separation of concerns
- **Smart backend workflows** with orchestration and automation
- **Real-time pricing automation** with immediate rule application
- **Advanced data engineering** with cleaning, analysis, and ML
- **LLM integration** for intelligent pricing recommendations
- **Enterprise-grade patterns** (auth, monitoring, testing, documentation)

Perfect for showcasing: **scraping, ETL, rule engines, scheduling, LLM integration, MongoDB operations, API contracts, and authentication** in a production-ready system.

## 🚀 Getting Started

See our [deployment guide](docs/deployment/guide.md) for detailed setup instructions and [API documentation](docs/api/endpoints.md) for integration details.

### Frontend (React 18 + Material-UI)
- **Modern UI**: Clean, responsive design with Material-UI components
- **Authentication**: JWT-based auth with refresh token handling
- **Dashboard**: Real-time analytics with interactive charts (Recharts)
- **Product Management**: Full CRUD operations with advanced filtering and search
- **Pricing Rules**: Visual pricing rule builder and management interface
- **Competitor Tracking**: Comprehensive competitor analysis and price comparison
- **Analytics**: Advanced data visualization with revenue, margin, and performance metrics

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

### Local Development

```bash
# Clone the repository
git clone https://github.com/dirshaye/OmniPriceX.git
cd OmniPriceX

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Generate gRPC code
chmod +x scripts/generate_grpc.sh
./scripts/generate_grpc.sh

# Start all services with Docker Compose
docker-compose up -d

# Or run individual services for development
cd services/api-gateway && python main.py
cd services/product-service && python main.py
cd services/pricing-service && python main.py
# ... etc
```

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Open http://localhost:3000 in your browser
```

The frontend includes:
- **Dashboard**: Interactive analytics and key metrics
- **Products**: Product management with CRUD operations
- **Pricing**: Pricing rules configuration and management
- **Competitors**: Competitor tracking and price comparison
- **Analytics**: Advanced data visualization and insights

**Technology Stack:**
- React 18 with functional components and hooks
- Material-UI for consistent design system
- React Router for navigation
- React Query for state management and API calls
- Recharts for data visualization
- JWT authentication with automatic token refresh

### Production Deployment on AWS

#### Prerequisites
- AWS CLI configured with appropriate permissions
- Terraform >= 1.0 installed
- Docker installed
- GitHub repository with secrets configured

#### Required GitHub Secrets
Configure these secrets in your GitHub repository settings:

```
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

#### One-Command Deployment

```bash
# Full deployment (infrastructure + services)
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# Or deploy specific components
./scripts/deploy.sh build          # Build and push images only
./scripts/deploy.sh infrastructure # Deploy infrastructure only
./scripts/deploy.sh grpc           # Generate gRPC code only
```

#### Manual Deployment Steps

1. **Initialize Terraform Backend**
   ```bash
   cd terraform
   terraform init
   ```

2. **Deploy Infrastructure**
   ```bash
   terraform plan
   terraform apply
   ```

3. **Build and Push Docker Images**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push each service
   docker build -t omnipricex-production-api-gateway ./services/api-gateway
   docker tag omnipricex-production-api-gateway:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/omnipricex-production-api-gateway:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/omnipricex-production-api-gateway:latest
   ```

#### CI/CD Pipeline

The project includes a GitHub Actions workflow that automatically:
- Runs tests on pull requests
- Builds and pushes Docker images on main branch pushes
- Deploys infrastructure using Terraform
- Updates ECS services with new images

#### Infrastructure Components

- **ECS Fargate**: Container orchestration
- **Application Load Balancer**: Traffic distribution
- **DocumentDB**: MongoDB-compatible database
- **ElastiCache Redis**: Caching and message queue
- **ECR**: Container registry
- **VPC**: Isolated network environment
- **Secrets Manager**: Secure credential storage

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