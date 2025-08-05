# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- AWS CLI configured
- Terraform installed
- Node.js 18+
- Python 3.11+

## Local Development

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/dirshaye/OmniPriceX.git
cd OmniPriceX

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Install dependencies
make install
```

### 2. Generate gRPC Code
```bash
make generate-proto
```

### 3. Start Services
```bash
make dev
```

This will start:
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- All microservices on ports 8001-8006

### 4. Health Check
```bash
curl http://localhost:8000/health
```

## Production Deployment

### 1. Infrastructure Setup
```bash
# Initialize Terraform
make terraform-init

# Plan infrastructure changes
make terraform-plan

# Apply infrastructure
cd infrastructure/terraform
terraform apply
```

### 2. Deploy Application
```bash
# Build and deploy
make deploy
```

### 3. Database Migration
```bash
# Run database migrations
./scripts/migrate.sh
```

## Environment Variables

### Required Variables
```bash
# Database
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_DB=omnipricex

# Redis
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Services URLs
PRODUCT_SERVICE_URL=localhost:50051
PRICING_SERVICE_URL=localhost:50052
# ... other services
```

### Optional Variables
```bash
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# External APIs
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
```

## Monitoring Setup

### Prometheus Configuration
Place in `monitoring/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
  
  - job_name: 'product-service'
    static_configs:
      - targets: ['product-service:8001']
```

### Grafana Dashboards
Import dashboards from `monitoring/grafana/dashboards/`

## Troubleshooting

### Common Issues

1. **gRPC Connection Failed**
   ```bash
   # Check if services are running
   docker-compose ps
   
   # Check service logs
   docker-compose logs product-service
   ```

2. **Database Connection Error**
   ```bash
   # Verify MongoDB connection
   mongosh "your-connection-string"
   ```

3. **Frontend Build Errors**
   ```bash
   # Clear npm cache
   cd frontend
   npm cache clean --force
   npm install
   ```

### Log Locations
- Application logs: `/var/log/omnipricex/`
- Container logs: `docker-compose logs [service-name]`
- System logs: `/var/log/syslog`

## Performance Tuning

### Database Optimization
- Create indexes for frequently queried fields
- Use connection pooling
- Enable read replicas for analytics

### Caching Strategy
- Implement Redis caching for frequently accessed data
- Use CDN for static assets
- Enable gzip compression

### Resource Allocation
- Monitor CPU and memory usage
- Set appropriate container limits
- Configure auto-scaling policies
