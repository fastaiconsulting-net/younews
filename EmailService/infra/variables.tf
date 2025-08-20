variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "project" {
  description = "Base name for resources"
  type        = string
  default     = "subscriptions-api"
}

variable "subs_table_name" {
  description = "DynamoDB table for email->topics"
  type        = string
  default     = "subscriptions"
}

variable "index_table_name" {
  description = "DynamoDB table for topic->emails"
  type        = string
  default     = "topic_index"
}

variable "image_tag" {
  description = "ECR image tag to deploy"
  type        = string
  default     = "v1"
}

variable "architecture" {
  description = "Lambda architecture: x86_64 or arm64"
  type        = string
  default     = "x86_64"
  validation {
    condition     = contains(["x86_64", "arm64"], var.architecture)
    error_message = "architecture must be x86_64 or arm64."
  }
}

variable "logs_retention_days" {
  description = "CloudWatch Logs retention"
  type        = number
  default     = 14
}
