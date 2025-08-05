# Secrets Manager
resource "aws_secretsmanager_secret" "app_secrets" {
  name = "${local.name_prefix}-app-secrets"
  
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  
  secret_string = jsonencode({
    mongo_uri = "mongodb://${aws_docdb_cluster.main.master_username}:${random_password.docdb_password.result}@${aws_docdb_cluster.main.endpoint}:27017/omnipricex?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
    redis_url = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379"
    jwt_secret = random_password.jwt_secret.result
  })
}

resource "random_password" "jwt_secret" {
  length  = 32
  special = true
}

# S3 Bucket for Terraform State
resource "aws_s3_bucket" "terraform_state" {
  bucket = "${local.name_prefix}-terraform-state"

  tags = local.tags
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for Terraform state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name           = "${local.name_prefix}-terraform-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = local.tags
}
