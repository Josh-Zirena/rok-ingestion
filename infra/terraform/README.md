# Infrastructure - Terraform

This directory contains Terraform configuration for the ROK Ingestion infrastructure.

## Overview

- **S3 bucket**: Data lake with inbox/, raw/, and curated/ prefixes
- **ECR repository**: Stores the ingestion Lambda container image
- **IAM roles**: Lambda execution role with S3 read/write permissions
- **CloudWatch Logs**: Log group for Lambda execution
- **Lambda function**: Container-based ingestion service (conditional)
- **S3 notification**: Triggers Lambda on inbox/ uploads (conditional)

## Deployment Workflow

### First-time Setup

1. **Initialize Terraform**:

   ```bash
   cd infra/terraform
   terraform init
   ```

2. **Apply base infrastructure** (without Lambda):

   ```bash
   terraform apply
   ```

   This creates the S3 bucket and ECR repository.

3. **Build and push Docker image**:

   ```bash
   # Note the ECR repository URL from terraform output
   ECR_REPO=$(terraform output -raw ecr_repo_url)

   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO

   # Build and push from repo root
   cd ../../
   docker build -f docker/ingest/Dockerfile -t $ECR_REPO:latest .
   docker push $ECR_REPO:latest
   ```

4. **Deploy Lambda with image URI**:
   ```bash
   cd infra/terraform
   terraform apply -var="ingest_image_uri=$ECR_REPO:latest"
   ```

### Subsequent Updates

After updating the ingestion code, rebuild and push the image, then re-apply Terraform with the image URI.

## Configuration

Key variables in `variables.tf`:

- `aws_region`: AWS region (default: us-east-1)
- `project_name`: Project prefix for resources (default: rok-ingestion)
- `ingest_lambda_name`: Lambda function name (default: ingest_players)
- `ingest_image_uri`: ECR image URI (if empty, Lambda is NOT created)
- `log_retention_days`: CloudWatch log retention (default: 14)

## Conditional Lambda Creation

The Lambda function and S3 notification are **only created when `ingest_image_uri` is provided**.

This allows you to:

1. Provision the base infrastructure first
2. Build and push the container image
3. Deploy the Lambda in a second apply

## Outputs

After applying, Terraform outputs:

- `bucket_name`: S3 bucket name
- `ecr_repo_url`: Full ECR repository URL
- `ecr_repo_name`: ECR repository name
- `ingest_lambda_name`: Lambda function name
- `ingest_lambda_created`: Boolean indicating if Lambda was created

## Clean Up

To destroy all infrastructure:

```bash
terraform destroy
```

Note: The S3 bucket has `force_destroy = true` for POC purposes, so it will be deleted even if it contains data.
