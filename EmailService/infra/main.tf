terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.40"
    }
  }
}

provider "aws" {
  region = var.region
}

locals {
  project = var.project
}

data "aws_caller_identity" "current" {}

# ---------------------------
# SNS Topic for Newsletter
# ---------------------------
resource "aws_sns_topic" "newsletter" {
  name = "${local.project}-newsletter"
  
  # Enable raw message delivery for SQS
  delivery_policy = jsonencode({
    "http" : {
      "defaultHealthyRetryPolicy" : {
        "minDelayTarget" : 20,
        "maxDelayTarget" : 20,
        "numRetries" : 3,
        "numMaxDelayRetries" : 0,
        "numNoDelayRetries" : 0,
        "numMinDelayRetries" : 0,
        "backoffFunction" : "linear"
      },
      "disableSubscriptionOverrides" : false
    }
  })
}

# Allow the topic to be subscribed to by email
resource "aws_sns_topic_policy" "newsletter" {
  arn = aws_sns_topic.newsletter.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = "sns:Publish"
        Resource = aws_sns_topic.newsletter.arn
        Condition = {
          StringEquals = {
            "AWS:SourceOwner": data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

# ---------------------------
# SQS Queue for Subscription Management
# ---------------------------
resource "aws_sqs_queue" "subscription_dlq" {
  name = "${local.project}-subscription-dlq"
}

resource "aws_sqs_queue" "subscription_queue" {
  name = "${local.project}-subscription-queue"
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.subscription_dlq.arn
    maxReceiveCount     = 3
  })

  visibility_timeout_seconds = 30
  message_retention_seconds = 345600 # 4 days
  delay_seconds             = 0
}

# ---------------------------
# ECR Repo for Lambda image
# ---------------------------
resource "aws_ecr_repository" "api" {
  name                 = "${local.project}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = local.project
  }
}

# ---------------------------
# IAM for Lambda
# ---------------------------
data "aws_iam_policy_document" "lambda_trust" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_exec" {
  name               = "${local.project}-exec"
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json
  tags = { Project = local.project }
}

# Basic logs
resource "aws_iam_role_policy_attachment" "logs_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# SNS and SQS access
data "aws_iam_policy_document" "sns_sqs_access" {
  statement {
    sid    = "SNSAccess"
    effect = "Allow"
    actions = [
      "sns:Publish",
      "sns:Subscribe",
      "sns:Unsubscribe",
      "sns:ListSubscriptionsByTopic",
      "sns:GetTopicAttributes"
    ]
    resources = [
      aws_sns_topic.newsletter.arn
    ]
  }

  statement {
    sid    = "SQSAccess"
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [
      aws_sqs_queue.subscription_queue.arn,
      aws_sqs_queue.subscription_dlq.arn
    ]
  }
}

resource "aws_iam_policy" "sns_sqs_policy" {
  name   = "${local.project}-sns-sqs"
  policy = data.aws_iam_policy_document.sns_sqs_access.json
}

resource "aws_iam_role_policy_attachment" "sns_sqs_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.sns_sqs_policy.arn
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.project}"
  retention_in_days = var.logs_retention_days
}

# ---------------------------
# Lambda (container image)
# ---------------------------
resource "aws_lambda_function" "api" {
  function_name = local.project
  role          = aws_iam_role.lambda_exec.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"

  timeout      = 30
  memory_size  = 512
  architectures = [var.architecture]

  environment {
    variables = {
      APP_NAME = local.project
      SNS_TOPIC_ARN = aws_sns_topic.newsletter.arn
      SQS_QUEUE_URL = aws_sqs_queue.subscription_queue.url
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda
  ]

  tags = {
    Project = local.project
  }
}

# ---------------------------
# HTTP API (API Gateway v2)
# ---------------------------
resource "aws_apigatewayv2_api" "http" {
  name          = "${local.project}-http"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_credentials = false
    allow_headers     = ["*"]
    allow_methods     = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    allow_origins     = [
      "https://fastaiconsulting-net.github.io"
    ]
    expose_headers    = ["*"]
    max_age           = 300
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  payload_format_version = "2.0"
  integration_uri        = aws_lambda_function.api.invoke_arn
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "options" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "OPTIONS /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGwInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

# ---------------------------
# CloudWatch Alarms
# ---------------------------
resource "aws_sns_topic" "alerts" {
  name = "${local.project}-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "zach.wolpe@fastaiconsulting.net"
}

resource "aws_sns_topic_policy" "alerts" {
  arn = aws_sns_topic.alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}

# Alarm for subscription errors
resource "aws_cloudwatch_metric_alarm" "subscription_errors" {
  alarm_name          = "${local.project}-subscription-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "ApproximateNumberOfMessagesVisible"
  namespace          = "AWS/SQS"
  period             = "300"
  statistic          = "Average"
  threshold          = "10"
  alarm_description  = "High number of failed subscription operations detected"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    QueueName = aws_sqs_queue.subscription_dlq.name
  }
}

# Alarm for high subscription rate
resource "aws_cloudwatch_metric_alarm" "subscription_spike" {
  alarm_name          = "${local.project}-subscription-spike"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "NumberOfMessagesPublished"
  namespace          = "AWS/SNS"
  period             = "300"
  statistic          = "Sum"
  threshold          = "5"
  alarm_description  = "High number of subscription requests detected"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    TopicName = aws_sns_topic.newsletter.name
  }
}