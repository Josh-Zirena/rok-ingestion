# Frontend Deployment

This directory contains the deployment script for the frontend.

## Prerequisites

- Terraform infrastructure already applied (S3 bucket and CloudFront created)
- AWS CLI configured with appropriate credentials
- Node.js and npm installed

## Deployment

To deploy the frontend to S3 + CloudFront:

```bash
./scripts/deploy_frontend.sh
```

This script will:
1. Build the frontend for production
2. Update `.env.production` with the correct API URL
3. Sync files to S3 bucket
4. Invalidate CloudFront cache
5. Output the live frontend URL

## First-Time Infrastructure Setup

If the frontend infrastructure doesn't exist yet:

```bash
cd infra/terraform
terraform plan   # Review changes
terraform apply  # Create S3 bucket and CloudFront distribution
```

Then run the deployment script.

## Manual Deployment

If you prefer to deploy manually:

```bash
# Build
cd frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://YOUR-BUCKET-NAME/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR-DIST-ID --paths "/*"
```

## Cache Invalidation

CloudFront caches assets for performance. After deployment, the script automatically invalidates the cache, but it may take 5-10 minutes for changes to propagate globally.

To manually check invalidation status:

```bash
aws cloudfront get-invalidation --distribution-id DIST_ID --id INVALIDATION_ID
```
