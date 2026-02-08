variable "project_name" {
  description = "Project name used in resource naming"
  type        = string
  default     = "omniprice"
}

variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "availability_zone" {
  description = "Optional specific AZ for public subnet. Leave empty to auto-select first available."
  type        = string
  default     = ""
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Public subnet CIDR block"
  type        = string
  default     = "10.20.1.0/24"
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed to access EC2 SSH (example: 203.0.113.10/32)"
  type        = string
}

variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ec2_root_volume_size" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 16
}

variable "ec2_key_name" {
  description = "Existing AWS key pair name for SSH. Leave empty to disable SSH key auth."
  type        = string
  default     = ""
}

variable "enable_api_port" {
  description = "Expose backend API port 8000 to the public internet"
  type        = bool
  default     = true
}

variable "frontend_bucket_name" {
  description = "S3 bucket name for frontend hosting. Leave empty to auto-generate unique name."
  type        = string
  default     = ""
}

variable "frontend_force_destroy" {
  description = "Allow deleting non-empty frontend bucket on terraform destroy"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
