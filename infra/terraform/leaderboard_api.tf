# Leaderboard API Lambda deployment using ZIP packaging

# Create dist directory for Lambda ZIP artifacts
resource "null_resource" "dist_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/dist"
  }
}

# Package leaderboard_api source code as ZIP
data "archive_file" "leaderboard_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src/leaderboard_api"
  output_path = "${path.module}/dist/leaderboard_api.zip"
  
  depends_on = [null_resource.dist_dir]
}

# IAM role for leaderboard Lambda
resource "aws_iam_role" "leaderboard_lambda_role" {
  name = "${var.project_name}-leaderboard-lambda-role"

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

# CloudWatch Logs policy for leaderboard Lambda
resource "aws_iam_policy" "leaderboard_lambda_logs" {
  name        = "${var.project_name}-leaderboard-lambda-logs-policy"
  description = "Allows leaderboard Lambda to write CloudWatch logs"

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
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/leaderboard_api:*"
        ]
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# Attach logs policy to leaderboard Lambda role
resource "aws_iam_role_policy_attachment" "leaderboard_lambda_logs" {
  role       = aws_iam_role.leaderboard_lambda_role.name
  policy_arn = aws_iam_policy.leaderboard_lambda_logs.arn
}

# Athena permissions policy for leaderboard Lambda
resource "aws_iam_policy" "leaderboard_lambda_athena" {
  name        = "${var.project_name}-leaderboard-lambda-athena-policy"
  description = "Allows leaderboard Lambda to query Athena"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults"
        ]
        # TODO: Scope to specific workgroup/catalog when productionizing
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:GetPartition",
          "glue:GetPartitions"
        ]
        Resource = [
          "arn:aws:glue:${var.aws_region}:*:catalog",
          "arn:aws:glue:${var.aws_region}:*:database/rok_ingestion_data",
          "arn:aws:glue:${var.aws_region}:*:table/rok_ingestion_data/*"
        ]
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# Attach Athena policy to leaderboard Lambda role
resource "aws_iam_role_policy_attachment" "leaderboard_lambda_athena" {
  role       = aws_iam_role.leaderboard_lambda_role.name
  policy_arn = aws_iam_policy.leaderboard_lambda_athena.arn
}

# S3 permissions for Athena results and curated data
resource "aws_iam_policy" "leaderboard_lambda_s3" {
  name        = "${var.project_name}-leaderboard-lambda-s3-policy"
  description = "Allows leaderboard Lambda to access Athena results in S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.data_lake.arn}/athena-results/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = [
          "${aws_s3_bucket.data_lake.arn}/curated/*"
        ]
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# Attach S3 policy to leaderboard Lambda role
resource "aws_iam_role_policy_attachment" "leaderboard_lambda_s3" {
  role       = aws_iam_role.leaderboard_lambda_role.name
  policy_arn = aws_iam_policy.leaderboard_lambda_s3.arn
}

# CloudWatch log group for leaderboard Lambda
resource "aws_cloudwatch_log_group" "leaderboard_api" {
  name              = "/aws/lambda/leaderboard_api"
  retention_in_days = var.log_retention_days

  tags = {
    Project = var.project_name
  }
}

# Lambda function for leaderboard API
resource "aws_lambda_function" "leaderboard_api" {
  function_name    = "leaderboard_api"
  runtime          = "python3.11"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.leaderboard_zip.output_path
  source_code_hash = data.archive_file.leaderboard_zip.output_base64sha256
  role             = aws_iam_role.leaderboard_lambda_role.arn
  timeout          = 30
  memory_size      = 512

  environment {
    variables = {
      ATHENA_DATABASE    = "rok_ingestion_data"
      ATHENA_TABLE       = "rok_players_curated"
      ATHENA_RESULTS_S3  = "s3://${aws_s3_bucket.data_lake.bucket}/athena-results/"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.leaderboard_api,
    aws_iam_role_policy_attachment.leaderboard_lambda_logs,
    aws_iam_role_policy_attachment.leaderboard_lambda_athena,
    aws_iam_role_policy_attachment.leaderboard_lambda_s3
  ]

  tags = {
    Project = var.project_name
  }
}
