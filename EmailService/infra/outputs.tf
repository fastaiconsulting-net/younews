output "api_base_url" {
  description = "Base URL for API Gateway stage"
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "ecr_repository_url" {
  description = "URL of ECR repository"
  value       = aws_ecr_repository.api.repository_url
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for newsletter"
  value       = aws_sns_topic.newsletter.arn
}

output "sqs_queue_url" {
  description = "URL of the SQS queue for subscription management"
  value       = aws_sqs_queue.subscription_queue.url
}

output "sqs_dlq_url" {
  description = "URL of the SQS dead letter queue"
  value       = aws_sqs_queue.subscription_dlq.url
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.api.function_name
}