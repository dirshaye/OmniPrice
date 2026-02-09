data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.ec2_instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.app.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2.name
  key_name                    = var.ec2_key_name != "" ? var.ec2_key_name : null
  associate_public_ip_address = true

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    volume_size           = var.ec2_root_volume_size
    volume_type           = "gp3"
    delete_on_termination = true
  }

  user_data = <<-EOF2
    #!/bin/bash
    set -eux

    # Install Docker and AWS CLI
    apt-get update
    apt-get install -y docker.io docker-compose awscli
    systemctl enable docker
    systemctl start docker

    # Prepare application directory
    mkdir -p /opt/omniprice
    cd /opt/omniprice

    # Create a minimal docker-compose for the server
    # Note: In a real CI/CD, this file would be copied or pulled from Git
    cat <<DOCKEREOF > docker-compose.yml
    version: '3.8'
    services:
      redis:
        image: redis:7.2-alpine
        restart: always
      rabbitmq:
        image: rabbitmq:3-management
        restart: always
      backend:
        image: ${aws_ecr_repository.backend.repository_url}:latest
        ports:
          - "8000:8000"
        environment:
          - REDIS_URL=redis://redis:6379/0
          - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
          - MONGODB_URL=mongodb+srv://dirshaye:iAhhsM8h2U9ZEEmC@omnipricecluster.i8uztyr.mongodb.net/
          - MONGODB_DB_NAME=omnipricex
          - SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
          - GEMINI_API_KEY=AIzaSyBvGsxRjy6M8v4DfdjR_Esb1rgir-ETdPk
        depends_on:
          - redis
          - rabbitmq
        restart: always
      scrape-worker:
        image: ${aws_ecr_repository.worker.repository_url}:latest
        environment:
          - REDIS_URL=redis://redis:6379/0
          - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
          - MONGODB_URL=mongodb+srv://dirshaye:iAhhsM8h2U9ZEEmC@omnipricecluster.i8uztyr.mongodb.net/
          - MONGODB_DB_NAME=omnipricex
          - GEMINI_API_KEY=AIzaSyBvGsxRjy6M8v4DfdjR_Esb1rgir-ETdPk
        command: python -m omniprice.workers.scrape_consumer
        depends_on:
          - rabbitmq
        restart: always
    DOCKEREOF

    # Login to ECR and Pull images
    aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin ${aws_ecr_repository.backend.repository_url}
    
    # Start the stack
    docker-compose up -d
  EOF2

  tags = merge(local.common_tags, { Name = "${local.name_prefix}-ec2" })
}
