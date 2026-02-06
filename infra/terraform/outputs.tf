output "bucket_name" {
  description = "Name of the S3 data lake bucket"
  value       = aws_s3_bucket.data_lake.bucket
}

output "ecr_repo_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.ingest.repository_url
}

output "ecr_repo_name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.ingest.name
}

output "ingest_lambda_name" {
  description = "Name of the ingestion Lambda function"
  value       = var.ingest_lambda_name
}

output "ingest_lambda_arn" {
  description = "ARN of the ingestion Lambda function"
  value       = aws_lambda_function.ingest.arn
}

output "codebuild_project_name" {
  description = "Name of the CodeBuild project for building Docker images"
  value       = aws_codebuild_project.ingest_image.name
}

output "codebuild_project_arn" {
  description = "ARN of the CodeBuild project"
  value       = aws_codebuild_project.ingest_image.arn
}

output "leaderboard_api_url" {
  description = "URL of the leaderboard API endpoint"
  value       = aws_apigatewayv2_api.leaderboard_http.api_endpoint
}

output "leaderboard_api_id" {
  description = "ID of the API Gateway HTTP API"
  value       = aws_apigatewayv2_api.leaderboard_http.id
}

output "frontend_bucket_name" {
  description = "Name of the S3 bucket hosting the frontend"
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_bucket_website_endpoint" {
  description = "Website endpoint for the S3 bucket"
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "frontend_url" {
  description = "Full HTTPS URL for the frontend (CloudFront)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}
