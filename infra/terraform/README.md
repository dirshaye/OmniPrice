# OmniPrice AWS Terraform

This Terraform stack provisions a low-cost AWS baseline for OmniPrice:

- VPC + public subnet + internet gateway
- Security group (SSH, HTTP/HTTPS, optional API 8000)
- EC2 instance (Docker host for backend/worker/frontend)
- IAM role/profile for SSM + CloudWatch agent
- S3 bucket for static frontend hosting

## Files

- `versions.tf`: Terraform and provider versions
- `variables.tf`: configurable values
- `network.tf`: VPC/subnet/route
- `security.tf`: security group rules
- `iam.tf`: EC2 role + instance profile
- `compute.tf`: EC2 instance + bootstrap
- `s3_frontend.tf`: S3 static website bucket
- `outputs.tf`: useful outputs

## Usage

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

Or use project script from repo root:

```bash
./scripts/deploy.sh plan
./scripts/deploy.sh apply
```

## Cost Notes

- Keep one `t3.micro` and stop/destroy when not used.
- No NAT Gateway or Load Balancer included (to avoid hourly costs).
- S3 bucket has storage + transfer costs; keep assets small.
- CloudWatch logs can grow cost if retention is not managed.

## Frontend Upload Example

```bash
aws s3 sync frontend/build/ s3://<frontend_bucket_name> --delete
```

After upload, use `frontend_website_url` output.
