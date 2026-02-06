# API Gateway HTTP API for Leaderboard Service

# HTTP API
resource "aws_apigatewayv2_api" "leaderboard_http" {
  name          = "rok-leaderboard-http"
  protocol_type = "HTTP"
  description   = "Public HTTP API for RoK player leaderboard queries"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }

  tags = {
    Project = var.project_name
  }
}

# Lambda integration
resource "aws_apigatewayv2_integration" "leaderboard_lambda" {
  api_id             = aws_apigatewayv2_api.leaderboard_http.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.leaderboard_api.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

# GET /leaderboard route
resource "aws_apigatewayv2_route" "get_leaderboard" {
  api_id    = aws_apigatewayv2_api.leaderboard_http.id
  route_key = "GET /leaderboard"
  target    = "integrations/${aws_apigatewayv2_integration.leaderboard_lambda.id}"
}

# GET /health route
resource "aws_apigatewayv2_route" "health_check" {
  api_id    = aws_apigatewayv2_api.leaderboard_http.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.leaderboard_lambda.id}"
}

# OPTIONS /{proxy+} route for CORS preflight
resource "aws_apigatewayv2_route" "cors_preflight" {
  api_id    = aws_apigatewayv2_api.leaderboard_http.id
  route_key = "OPTIONS /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.leaderboard_lambda.id}"
}

# Default stage with auto-deploy and throttling
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.leaderboard_http.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 10
    throttling_rate_limit  = 5
  }

  tags = {
    Project = var.project_name
  }
}

# Lambda permission for API Gateway to invoke the function
resource "aws_lambda_permission" "apigw_invoke_leaderboard" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.leaderboard_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.leaderboard_http.execution_arn}/*/*"
}
