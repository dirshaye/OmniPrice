output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}

output "ec2_public_ip" {
  description = "Public IP address of EC2 instance"
  value       = aws_instance.app.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of EC2 instance"
  value       = aws_instance.app.public_dns
}

output "frontend_bucket_name" {
  description = "S3 bucket name for frontend hosting"
  value       = aws_s3_bucket.frontend.id
}

output "frontend_website_url" {
  description = "S3 static website endpoint"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "ecr_repository_url_backend" {
  description = "ECR repository URL for backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_repository_url_worker" {
  description = "ECR repository URL for scrape worker"
  value       = aws_ecr_repository.worker.repository_url
}
