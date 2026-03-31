# ─────────────────────────────────────────────────────────────
# ClearCause MVP — Terraform Infrastructure (us-east-1)
# Serverless-first: Lambda + API Gateway + S3 + DynamoDB + SQS
# ─────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "clearcause-terraform-state"
    key    = "mvp/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "ClearCause"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ─── Variables ───
variable "aws_region" { default = "us-east-1" }
variable "environment" { default = "dev" }
variable "openai_api_key" { sensitive = true }
variable "domain_name" { default = "" }

locals {
  prefix = "clearcause-${var.environment}"
}

# ─── S3: Document Storage ───
resource "aws_s3_bucket" "documents" {
  bucket = "${local.prefix}-documents"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    id     = "archive-old-reports"
    status = "Enabled"
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket                  = aws_s3_bucket.documents.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ─── S3: Frontend Hosting ───
resource "aws_s3_bucket" "frontend" {
  bucket = "${local.prefix}-frontend"
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  index_document { suffix = "index.html" }
  error_document { key = "index.html" }
}

# ─── CloudFront ───
resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket_website_configuration.frontend.website_endpoint
    origin_id   = "S3Frontend"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  enabled             = true
  default_root_object = "index.html"
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3Frontend"
    viewer_protocol_policy = "redirect-to-https"
    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
  }
  restrictions {
    geo_restriction { restriction_type = "none" }
  }
  viewer_certificate { cloudfront_default_certificate = true }
}

# ─── DynamoDB Tables ───
resource "aws_dynamodb_table" "jobs" {
  name         = "${local.prefix}-jobs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"

  attribute { name = "job_id"  type = "S" }
  attribute { name = "user_id" type = "S" }

  global_secondary_index {
    name            = "user-index"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  ttl { attribute_name = "ttl" enabled = true }
}

resource "aws_dynamodb_table" "results" {
  name         = "${local.prefix}-results"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"

  attribute { name = "job_id"  type = "S" }
  attribute { name = "user_id" type = "S" }

  global_secondary_index {
    name            = "user-index"
    hash_key        = "user_id"
    projection_type = "ALL"
  }
}

# ─── SQS: Analysis Queue ───
resource "aws_sqs_queue" "analysis" {
  name                       = "${local.prefix}-analysis-queue"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 86400
  receive_wait_time_seconds  = 10

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.analysis_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "analysis_dlq" {
  name                      = "${local.prefix}-analysis-dlq"
  message_retention_seconds = 604800  # 7 days
}

# ─── Cognito: User Auth ───
resource "aws_cognito_user_pool" "main" {
  name = "${local.prefix}-users"

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  auto_verified_attributes = ["email"]

  schema {
    attribute_data_type = "String"
    name                = "email"
    required            = true
    mutable             = true
  }
}

resource "aws_cognito_user_pool_client" "web" {
  name         = "${local.prefix}-web-client"
  user_pool_id = aws_cognito_user_pool.main.id

  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
  ]
}

# ─── IAM: Lambda Execution Role ───
resource "aws_iam_role" "lambda_exec" {
  name = "${local.prefix}-lambda-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.prefix}-lambda-policy"
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = "${aws_s3_bucket.documents.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query"]
        Resource = [aws_dynamodb_table.jobs.arn, aws_dynamodb_table.results.arn, "${aws_dynamodb_table.jobs.arn}/index/*", "${aws_dynamodb_table.results.arn}/index/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["sqs:SendMessage", "sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
        Resource = aws_sqs_queue.analysis.arn
      },
      {
        Effect   = "Allow"
        Action   = ["textract:StartDocumentTextDetection", "textract:GetDocumentTextDetection"]
        Resource = "*"
      },
    ]
  })
}

# ─── Secrets Manager: API Keys ───
resource "aws_secretsmanager_secret" "openai_key" {
  name = "${local.prefix}-openai-api-key"
}

resource "aws_secretsmanager_secret_version" "openai_key" {
  secret_id     = aws_secretsmanager_secret.openai_key.id
  secret_string = var.openai_api_key
}

# ─── Lambda Functions ───
resource "aws_lambda_function" "upload" {
  function_name = "${local.prefix}-upload"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256
  filename      = "${path.module}/../backend/lambdas/upload/package.zip"

  environment {
    variables = {
      DOCUMENTS_BUCKET = aws_s3_bucket.documents.id
      JOBS_TABLE       = aws_dynamodb_table.jobs.name
      QUEUE_URL        = aws_sqs_queue.analysis.url
    }
  }
}

resource "aws_lambda_function" "analyze" {
  function_name = "${local.prefix}-analyze"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 1024
  filename      = "${path.module}/../backend/lambdas/analyze/package.zip"

  environment {
    variables = {
      DOCUMENTS_BUCKET = aws_s3_bucket.documents.id
      JOBS_TABLE       = aws_dynamodb_table.jobs.name
      RESULTS_TABLE    = aws_dynamodb_table.results.name
      OPENAI_API_KEY   = var.openai_api_key
    }
  }
}

resource "aws_lambda_function" "report" {
  function_name = "${local.prefix}-report"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 512
  filename      = "${path.module}/../backend/lambdas/report/package.zip"

  environment {
    variables = {
      DOCUMENTS_BUCKET = aws_s3_bucket.documents.id
      RESULTS_TABLE    = aws_dynamodb_table.results.name
    }
  }
}

# ─── SQS → Lambda Trigger ───
resource "aws_lambda_event_source_mapping" "analysis_trigger" {
  event_source_arn = aws_sqs_queue.analysis.arn
  function_name    = aws_lambda_function.analyze.arn
  batch_size       = 1
}

# ─── API Gateway ───
resource "aws_apigatewayv2_api" "main" {
  name          = "${local.prefix}-api"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 3600
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.main.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito"
  jwt_configuration {
    audience = [aws_cognito_user_pool_client.web.id]
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.main.id}"
  }
}

# API Routes
resource "aws_apigatewayv2_integration" "upload" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.upload.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "upload" {
  api_id             = aws_apigatewayv2_api.main.id
  route_key          = "POST /api/upload"
  target             = "integrations/${aws_apigatewayv2_integration.upload.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_integration" "report" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.report.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "report" {
  api_id             = aws_apigatewayv2_api.main.id
  route_key          = "GET /api/report"
  target             = "integrations/${aws_apigatewayv2_integration.report.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "upload_apigw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.upload.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "report_apigw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.report.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# ─── Outputs ───
output "api_url" { value = aws_apigatewayv2_api.main.api_endpoint }
output "frontend_url" { value = "https://${aws_cloudfront_distribution.frontend.domain_name}" }
output "cognito_user_pool_id" { value = aws_cognito_user_pool.main.id }
output "cognito_client_id" { value = aws_cognito_user_pool_client.web.id }
output "documents_bucket" { value = aws_s3_bucket.documents.id }
