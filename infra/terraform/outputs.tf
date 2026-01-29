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

output "ingest_lambda_created" {
  description = "Whether the ingestion Lambda was created"
  value       = local.create_ingest_lambda
}

output "codebuild_project_name" {
  description = "Name of the CodeBuild project for building Docker images"
  value       = aws_codebuild_project.ingest_image.name
}

output "codebuild_project_arn" {
  description = "ARN of the CodeBuild project"
  value       = aws_codebuild_project.ingest_image.arn
}
