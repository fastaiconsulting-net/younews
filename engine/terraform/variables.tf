variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"  # Change this to your preferred region
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "younews-api"
}

variable "environment" {
  description = "Environment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "ecr_repository_url" {
  description = "ECR repository URL for the Lambda container image"
  type        = string
}

variable "ecr_image_tag" {
  description = "ECR image tag to deploy"
  type        = string
  default     = "latest"
}

variable "lambda_memory" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 1024
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "initial_secrets" {
  description = "Initial secrets to store in AWS Secrets Manager"
  type        = map(string)
  sensitive   = true
  default     = {}
}
