provider "aws" {
  region = var.aws_region
}

provider "random" {}

locals {
  create_ingest_lambda = var.ingest_image_uri != ""
}

# Create a unique suffix for the bucket name
resource "random_pet" "bucket_suffix" {
  length = 2
}

# S3 bucket for data lake
resource "aws_s3_bucket" "data_lake" {
  bucket        = "${var.project_name}-${random_pet.bucket_suffix.id}"
  force_destroy = true # POC only - allows deletion of non-empty bucket

  tags = {
    Project = var.project_name
  }
}

# ECR repository for ingestion Lambda container image
resource "aws_ecr_repository" "ingest" {
  name                 = "${var.project_name}-ingest"
  image_tag_mutability = "MUTABLE" # POC - allow tag overwriting

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = var.project_name
  }
}

# IAM role for ingestion Lambda
resource "aws_iam_role" "ingest_lambda" {
  name = "${var.project_name}-ingest-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# IAM policy for Lambda S3 access
resource "aws_iam_policy" "ingest_lambda_s3" {
  name        = "${var.project_name}-ingest-lambda-s3-policy"
  description = "Allows ingestion Lambda to read from inbox and write to raw/curated"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = [
          "${aws_s3_bucket.data_lake.arn}/inbox/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.data_lake.arn}/raw/*",
          "${aws_s3_bucket.data_lake.arn}/curated/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn
        ]
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# Attach S3 policy to Lambda role
resource "aws_iam_role_policy_attachment" "ingest_lambda_s3" {
  role       = aws_iam_role.ingest_lambda.name
  policy_arn = aws_iam_policy.ingest_lambda_s3.arn
}

# IAM policy for Lambda CloudWatch Logs
resource "aws_iam_policy" "ingest_lambda_logs" {
  name        = "${var.project_name}-ingest-lambda-logs-policy"
  description = "Allows ingestion Lambda to write CloudWatch logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.ingest_lambda_name}:*"
        ]
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# Attach logs policy to Lambda role
resource "aws_iam_role_policy_attachment" "ingest_lambda_logs" {
  role       = aws_iam_role.ingest_lambda.name
  policy_arn = aws_iam_policy.ingest_lambda_logs.arn
}

# CloudWatch log group for ingestion Lambda
resource "aws_cloudwatch_log_group" "ingest_lambda" {
  name              = "/aws/lambda/${var.ingest_lambda_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Project = var.project_name
  }
}

# Lambda function (conditional - only created when image_uri is provided)
resource "aws_lambda_function" "ingest" {
  count = local.create_ingest_lambda ? 1 : 0

  function_name = var.ingest_lambda_name
  package_type  = "Image"
  image_uri     = var.ingest_image_uri
  role          = aws_iam_role.ingest_lambda.arn
  timeout       = 60
  memory_size   = 1024

  environment {
    variables = {
      BUCKET_NAME    = aws_s3_bucket.data_lake.bucket
      SOURCE_NAME    = "rok_players"
      RAW_PREFIX     = "raw/"
      CURATED_PREFIX = "curated/"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.ingest_lambda
  ]

  tags = {
    Project = var.project_name
  }
}

# Lambda permission for S3 to invoke (conditional)
resource "aws_lambda_permission" "allow_s3" {
  count = local.create_ingest_lambda ? 1 : 0

  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest[0].function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.data_lake.arn
}

# S3 bucket notification to trigger Lambda (conditional)
resource "aws_s3_bucket_notification" "inbox_trigger" {
  count = local.create_ingest_lambda ? 1 : 0

  bucket = aws_s3_bucket.data_lake.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingest[0].arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "inbox/"
  }

  depends_on = [
    aws_lambda_permission.allow_s3
  ]
}

# IAM role for CodeBuild
resource "aws_iam_role" "codebuild" {
  name = "${var.project_name}-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# IAM policy for CodeBuild to access ECR
resource "aws_iam_policy" "codebuild_ecr" {
  name        = "${var.project_name}-codebuild-ecr-policy"
  description = "Allows CodeBuild to push images to ECR"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = aws_ecr_repository.ingest.arn
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# Attach ECR policy to CodeBuild role
resource "aws_iam_role_policy_attachment" "codebuild_ecr" {
  role       = aws_iam_role.codebuild.name
  policy_arn = aws_iam_policy.codebuild_ecr.arn
}

# IAM policy for CodeBuild CloudWatch Logs
resource "aws_iam_policy" "codebuild_logs" {
  name        = "${var.project_name}-codebuild-logs-policy"
  description = "Allows CodeBuild to write CloudWatch logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/codebuild/${var.project_name}-*"
        ]
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# Attach logs policy to CodeBuild role
resource "aws_iam_role_policy_attachment" "codebuild_logs" {
  role       = aws_iam_role.codebuild.name
  policy_arn = aws_iam_policy.codebuild_logs.arn
}

# CodeBuild project for building and pushing Docker image
resource "aws_codebuild_project" "ingest_image" {
  name          = "${var.project_name}-ingest-image-build"
  description   = "Builds and pushes the ingestion Lambda Docker image to ECR"
  service_role  = aws_iam_role.codebuild.arn
  build_timeout = 20 # minutes

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    privileged_mode             = true # Required for Docker builds
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = data.aws_caller_identity.current.account_id
    }

    environment_variable {
      name  = "IMAGE_REPO_NAME"
      value = aws_ecr_repository.ingest.name
    }
  }

  source {
    type      = var.source_repo_url != "" ? "GITHUB" : "NO_SOURCE"
    location  = var.source_repo_url != "" ? var.source_repo_url : null
    buildspec = file("${path.module}/../../buildspec.yml")
    
    git_clone_depth = 1
    
    dynamic "git_submodules_config" {
      for_each = var.source_repo_url != "" ? [1] : []
      content {
        fetch_submodules = false
      }
    }
  }

  source_version = var.source_repo_url != "" ? var.source_repo_branch : null

  tags = {
    Project = var.project_name
  }
}

# Data source to get current AWS account ID
data "aws_caller_identity" "current" {}
