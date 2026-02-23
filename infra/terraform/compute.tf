# EC2 Instance for OmniPrice

resource "aws_security_group" "app" {
  name        = "${local.name_prefix}-app-sg"
  description = "Allow inbound traffic for OmniPrice"
  vpc_id      = aws_vpc.main.id

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # FastAPI
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.ec2_instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.app.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2.name
  associate_public_ip_address = true

  root_block_device {
    volume_size = 16
    volume_type = "gp3"
  }

  user_data = <<-EOF
    #!/bin/bash
    set -eux

    # Install Docker & Compose
    apt-get update
    apt-get install -y docker.io docker-compose git awscli
    systemctl enable docker
    systemctl start docker

    # Setup App
    mkdir -p /app
    cd /app
    git clone https://github.com/dirshaye/OmniPrice.git .
    
    # We use local docker-compose.yml which includes RabbitMQ & Redis
    # Pull secrets from SSM
    export MONGODB_URL=$(aws ssm get-parameter --name "/omniprice/prod/MONGODB_URL" --with-decryption --region eu-central-1 --query "Parameter.Value" --output text)
    export GEMINI_API_KEY=$(aws ssm get-parameter --name "/omniprice/prod/GEMINI_API_KEY" --with-decryption --region eu-central-1 --query "Parameter.Value" --output text)

    # Generate .env file for Docker Compose
    cat <<ENVEOF > .env
MONGODB_URL=$MONGODB_URL
MONGODB_DB_NAME=omnipricex
GEMINI_API_KEY=$GEMINI_API_KEY
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
ENVEOF

    docker-compose up -d --build
  EOF

  tags = merge(local.common_tags, { Name = "${local.name_prefix}-ec2" })
}
