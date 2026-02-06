#!/bin/bash
# Deploy frontend to S3 and invalidate CloudFront cache

set -e

echo "=========================================="
echo "Frontend Deployment Script"
echo "=========================================="

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Get infrastructure outputs
echo "📋 Getting infrastructure details..."
cd infra/terraform

BUCKET_NAME=$(terraform output -raw frontend_bucket_name 2>/dev/null)
DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id 2>/dev/null)
CLOUDFRONT_URL=$(terraform output -raw frontend_url 2>/dev/null)

if [ -z "$BUCKET_NAME" ]; then
  echo "❌ Error: Frontend infrastructure not deployed yet"
  echo "Run 'terraform apply' first to create the S3 bucket and CloudFront distribution"
  exit 1
fi

echo "✅ S3 Bucket: $BUCKET_NAME"
echo "✅ CloudFront ID: $DISTRIBUTION_ID"
echo "✅ Frontend URL: $CLOUDFRONT_URL"

# Update production environment variable
cd "$PROJECT_ROOT/frontend"
API_URL=$(cd ../infra/terraform && terraform output -raw leaderboard_api_url)
echo "VITE_API_URL=$API_URL" > .env.production

echo ""
echo "🏗️  Building frontend for production..."
npm run build

if [ ! -d "dist" ]; then
  echo "❌ Error: Build failed - dist/ directory not found"
  exit 1
fi

echo ""
echo "📤 Uploading to S3..."
aws s3 sync dist/ "s3://$BUCKET_NAME/" \
  --delete \
  --cache-control "public, max-age=3600" \
  --exclude "*.html" \
  --exclude "*.json"

# Upload HTML files with no-cache to ensure updates are immediate
aws s3 sync dist/ "s3://$BUCKET_NAME/" \
  --exclude "*" \
  --include "*.html" \
  --cache-control "no-cache, no-store, must-revalidate"

echo ""
echo "♻️  Invalidating CloudFront cache..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id "$DISTRIBUTION_ID" \
  --paths "/*" \
  --query 'Invalidation.Id' \
  --output text)

echo "✅ Invalidation created: $INVALIDATION_ID"

echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo "Frontend URL: $CLOUDFRONT_URL"
echo ""
echo "Note: CloudFront cache invalidation may take a few minutes to propagate."
echo "You can check the status with:"
echo "  aws cloudfront get-invalidation --distribution-id $DISTRIBUTION_ID --id $INVALIDATION_ID"
