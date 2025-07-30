# OmniPriceX Deployment Checklist

## Pre-deployment Setup

### 1. GitHub Repository Setup
- [ ] Repository is public/private as needed
- [ ] All code is committed and pushed to main branch
- [ ] Repository secrets are configured:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY` 
  - [ ] `GEMINI_API_KEY`

### 2. AWS Account Preparation
- [ ] AWS CLI is installed and configured
- [ ] IAM user has necessary permissions:
  - [ ] EC2 (ECS, ECR)
  - [ ] VPC
  - [ ] DocumentDB
  - [ ] ElastiCache
  - [ ] Secrets Manager
  - [ ] S3
  - [ ] DynamoDB
  - [ ] Application Load Balancer
- [ ] Terraform state S3 bucket exists (or will be created)

### 3. Local Development Environment
- [ ] Docker is installed and running
- [ ] Python 3.11+ is installed
- [ ] Terraform is installed
- [ ] AWS CLI is configured
- [ ] `.env` file is created from `.env.example`
- [ ] All required API keys are obtained

## Deployment Steps

### Local Development
1. [ ] Clone repository
2. [ ] Run `make setup-env` to create .env file
3. [ ] Run `make grpc` to generate protobuf code
4. [ ] Run `make deploy-local` to start all services
5. [ ] Verify all services are running with `make check-services`
6. [ ] Test API endpoints

### AWS Production Deployment

#### Option 1: Automated Deployment
1. [ ] Push code to main branch
2. [ ] GitHub Actions will automatically:
   - [ ] Run tests
   - [ ] Build and push Docker images
   - [ ] Deploy infrastructure
   - [ ] Update services

#### Option 2: Manual Deployment
1. [ ] Run `make deploy-aws` for full deployment
2. [ ] Or use individual commands:
   - [ ] `make grpc` - Generate protobuf code
   - [ ] `make docker-login` - Login to ECR
   - [ ] `make terraform-init` - Initialize Terraform
   - [ ] `make terraform-plan` - Review infrastructure changes
   - [ ] `make terraform-apply` - Deploy infrastructure

## Post-deployment Verification

### Infrastructure Verification
- [ ] ECS cluster is running
- [ ] All services are running in ECS
- [ ] Load balancer is healthy
- [ ] DocumentDB cluster is accessible
- [ ] Redis cluster is accessible
- [ ] ECR repositories contain images

### Application Verification
- [ ] API Gateway responds at load balancer URL
- [ ] Health check endpoint returns 200
- [ ] Product service gRPC endpoints work
- [ ] Database connections are successful
- [ ] Inter-service communication works

### Security Verification
- [ ] Security groups are properly configured
- [ ] Secrets are stored in AWS Secrets Manager
- [ ] No sensitive data in environment variables
- [ ] VPC and subnets are correctly isolated

## Monitoring and Maintenance

### Set up monitoring
- [ ] CloudWatch logs are being generated
- [ ] ECS service metrics are available
- [ ] Set up alarms for critical metrics
- [ ] Document baseline performance metrics

### Backup and Recovery
- [ ] DocumentDB automated backups are enabled
- [ ] Terraform state is backed up
- [ ] Deployment rollback procedure is documented

## Troubleshooting

### Common Issues
1. **ECS services not starting**
   - Check CloudWatch logs
   - Verify environment variables
   - Check security group rules

2. **Database connection issues**
   - Verify DocumentDB security group allows ECS access
   - Check connection string format
   - Ensure cluster is in correct VPC

3. **Load balancer health checks failing**
   - Verify health check endpoint is implemented
   - Check target group configuration
   - Ensure services are listening on correct ports

4. **Docker image build failures**
   - Check Dockerfile syntax
   - Verify all dependencies are available
   - Check shared proto file copying

### Rollback Procedure
1. [ ] Identify previous working commit hash
2. [ ] Run deployment with previous image tag:
   ```bash
   cd terraform
   terraform apply -var="image_tag=<previous-commit-hash>"
   ```
3. [ ] Verify services are running correctly
4. [ ] Update application code and redeploy when ready

## Environment Variables Reference

### Required for all environments
- `MONGO_URI` - Database connection string
- `JWT_SECRET` - Secret for JWT token signing
- `GEMINI_API_KEY` - Google Gemini API key

### Required for production
- `AWS_REGION` - AWS deployment region
- Service host variables for inter-service communication

### Optional
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging verbosity
