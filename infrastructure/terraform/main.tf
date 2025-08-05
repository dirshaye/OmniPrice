terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "omnipricex-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "omnipricex"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  services = [
    "api-gateway",
    "product-service", 
    "pricing-service",
    "scraper-service",
    "competitor-service",
    "llm-assistant-service",
    "auth-service"
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
