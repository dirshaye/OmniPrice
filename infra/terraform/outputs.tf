output "ec2_public_ip" {
  description = "Public IP of the server"
  value       = aws_instance.app.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of the server"
  value       = aws_instance.app.public_dns
}

output "frontend_website_url" {
  description = "S3 static website endpoint"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "github_actions_access_key_id" {
  value = aws_iam_access_key.github_actions.id
}

output "github_actions_secret_access_key" {
  value     = aws_iam_access_key.github_actions.secret
  sensitive = true
}
