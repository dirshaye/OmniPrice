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