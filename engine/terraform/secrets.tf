resource "aws_secretsmanager_secret" "app_secrets" {
  name = "${var.app_name}-${var.environment}-secrets"
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Initial secret version using values from tfvars
resource "aws_secretsmanager_secret_version" "app_secrets_version" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode(merge(var.initial_secrets, {
    APP_SECRET_NAME = aws_secretsmanager_secret.app_secrets.name
  }))
}

# IAM policy for accessing secrets
data "aws_iam_policy_document" "secrets_access" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [
      aws_secretsmanager_secret.app_secrets.arn
    ]
  }
}
