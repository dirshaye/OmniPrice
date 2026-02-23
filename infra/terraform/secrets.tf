# Secure Secret Storage (SSM Parameter Store)

resource "aws_ssm_parameter" "mongodb_url" {
  name        = "/omniprice/prod/MONGODB_URL"
  description = "MongoDB Connection String"
  type        = "SecureString"
  value       = "CHANGE_ME_IN_AWS_CONSOLE" # Placeholder

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "gemini_api_key" {
  name        = "/omniprice/prod/GEMINI_API_KEY"
  description = "Google Gemini API Key"
  type        = "SecureString"
  value       = "CHANGE_ME_IN_AWS_CONSOLE" # Placeholder

  lifecycle {
    ignore_changes = [value]
  }
}
