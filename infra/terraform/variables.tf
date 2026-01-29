variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "rok-ingestion"
}

variable "ingest_lambda_name" {
  description = "Name of the ingestion Lambda function"
  type        = string
  default     = "ingest_players"
}

variable "ingest_image_uri" {
  description = "ECR image URI for ingestion Lambda. If empty, Lambda and S3 notifications will not be created."
  type        = string
  default     = ""
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "source_repo_url" {
  description = "Git repository URL for CodeBuild source (optional - leave empty to upload source manually)"
  type        = string
  default     = ""
}

variable "source_repo_branch" {
  description = "Git branch for CodeBuild to build from"
  type        = string
  default     = "main"
}
