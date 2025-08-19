# Younews News Agent

Younews runs daily on AWS trigger by a cron job.

## Deployment

1. Push to ECR

```zsh
# set env vars
export ECR_URL=084285615195.dkr.ecr.eu-west-2.amazonaws.com/younews-api
export IMAGE_NAME=younews
export IMAGE_TAG=v1
echo ------------------------------------------------
echo ECR_URL: $ECR_URL
echo image name: $IMAGE_NAME
echo image tag: $IMAGE_TAG
echo ------------------------------------------------


# build & push image
docker buildx build --platform linux/amd64 --load -t ${ECR_URL}:${IMAGE_TAG} .

aws ecr get-login-password --region eu-west-2 \
| docker login --username AWS --password-stdin $(echo $ECR_URL | cut -d'/' -f1)

docker push ${ECR_URL}:${IMAGE_TAG}
```

2. Deploy Lambda & AWS Secrets with Terraform

```zsh
# Navigate to terraform directory
cd terraform

# Copy and configure terraform.tfvars
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your configuration and secrets

# Initialize Terraform
terraform init

# Review the deployment plan
terraform plan

# Apply the configuration
terraform apply -auto-approve

# After deployment, update the secrets in AWS Secrets Manager with your actual credentials
# The secret name will be output after terraform apply
```

## Configuration

### Environment Variables
Required for ECR image push:
- `ECR_URL`: Your ECR repository URL
- `IMAGE_TAG`: Docker image tag to deploy

### Terraform Variables (terraform.tfvars)
Configure these variables in your `terraform.tfvars` file:
- `aws_region`: AWS region for deployment (default: eu-west-2)
- `app_name`: Application name (default: younews-api)
- `environment`: Deployment environment (e.g., dev, prod)
- `ecr_repository_url`: Your ECR repository URL
- `ecr_image_tag`: Docker image tag to deploy
- `lambda_memory`: Lambda function memory in MB
- `lambda_timeout`: Lambda function timeout in seconds
- `initial_secrets`: Map of secrets to store in AWS Secrets Manager:
  ```hcl
  initial_secrets = {
    AWS_ACCESS_KEY_ID     = "your-access-key"
    AWS_SECRET_ACCESS_KEY = "your-secret-key"
    AWS_REGION           = "eu-west-2"
  }
  ```

Note: Never commit your `terraform.tfvars` file to version control as it contains sensitive information.

## Infrastructure Components

The deployment creates the following AWS resources:
- Lambda function with container image from ECR
- AWS Secrets Manager secret for credentials
- IAM roles and policies for Lambda execution
- Lambda Function URL for HTTP access

## Accessing the API

After deployment, the Lambda Function URL will be displayed in the Terraform outputs. You can use this URL to access the API endpoints:

- Health check: `GET {lambda_url}/healthz`
- Generate news report: `POST {lambda_url}/generate-news-report`

## Monitoring and Logs

Access Lambda logs through CloudWatch Logs:
1. Go to AWS CloudWatch console
2. Navigate to Log Groups
3. Find the log group named `/aws/lambda/younews-api-{environment}`