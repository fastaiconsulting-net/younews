# Newsletter API — SNS + FastAPI (Lambda)

Simple email newsletter subscription service using AWS SNS (Simple Notification Service) for managing subscriptions and sending emails.

## What it deploys

- **SNS Topic**
  - Handles email subscriptions with automatic confirmation
  - Manages unsubscribe requests
  - Sends newsletter emails
- **SQS Queue**
  - Handles subscription management operations
  - Includes Dead Letter Queue for failed operations
- **API**: FastAPI on AWS Lambda (container) via Mangum
- **HTTP API** (API Gateway v2)
- **ECR repo, IAM role, CloudWatch logs, SNS alerts**

## Layout

```
../.env
EmailService/
├─ app.py
├─ sns_manager.py
├─ requirements.txt
├─ Dockerfile
└─ infra/
   ├─ main.tf
   ├─ variables.tf
   └─ outputs.tf
```

## Environment (parent folder)

Create `../.env`:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=eu-west-2

# Infrastructure (available after terraform apply)
SNS_TOPIC_ARN=...          # SNS Topic ARN for newsletter
SQS_QUEUE_URL=...          # Main SQS Queue URL
SQS_DLQ_URL=...           # Dead Letter Queue URL
BASE_URL=...              # API Gateway URL
ECR_REPOSITORY_URL=...    # ECR Repository URL
LAMBDA_FUNCTION_NAME=...  # Lambda Function Name

# Optional
CREATE_TABLES_ON_START=false  # Set to true for local development
```

You can get these values after deployment using:
```bash
cd infra
terraform output
```

## Run locally

```bash
cd EmailService
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

## API (quick reference)

- `GET /healthz` — Health check
- `GET /subscriptions/{email}` — Get subscription status
- `POST /subscriptions/subscribe` — Subscribe an email (sends confirmation)
- `POST /subscriptions/unsubscribe` — Unsubscribe using subscription ARN
- `GET /subscriptions` — Get all confirmed subscriptions

### Example Usage

```bash
# Subscribe a user (will trigger confirmation email)
curl -X POST "http://localhost:8000/subscriptions/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Check subscription status
curl "http://localhost:8000/subscriptions/user@example.com"

# Unsubscribe a user (using subscription ARN)
curl -X POST "http://localhost:8000/subscriptions/unsubscribe" \
  -H "Content-Type: application/json" \
  -d '{"subscription_arn": "arn:aws:sns:..."}'

# Get all confirmed subscriptions
curl "http://localhost:8000/subscriptions"
```

## Deploy (Terraform + container)

### 1) Create ECR

```bash
cd EmailService/infra
terraform init
terraform apply -target=aws_ecr_repository.api -auto-approve
```

### 2) Build & push image

```bash
ECR_URL=$(terraform output -raw ecr_repository_url)
IMAGE_TAG=v1
cd ..
docker buildx build --platform linux/amd64 --load -t ${ECR_URL}:${IMAGE_TAG} .
aws ecr get-login-password --region eu-west-2 \
 | docker login --username AWS --password-stdin $(echo $ECR_URL | cut -d'/' -f1)
docker push ${ECR_URL}:${IMAGE_TAG}
```

### 3) Deploy infra + Lambda + API

```bash
cd infra
terraform apply -auto-approve -var="image_tag=${IMAGE_TAG}"

# Export all necessary environment variables
export BASE_URL=$(terraform output -raw api_base_url)
export SNS_TOPIC_ARN=$(terraform output -raw sns_topic_arn)
export SQS_QUEUE_URL=$(terraform output -raw sqs_queue_url)
export SQS_DLQ_URL=$(terraform output -raw sqs_dlq_url)
export ECR_REPOSITORY_URL=$(terraform output -raw ecr_repository_url)
export LAMBDA_FUNCTION_NAME=$(terraform output -raw lambda_function_name)

# Display the values
echo "Environment variables set:"
echo "BASE_URL=$BASE_URL"
echo "SNS_TOPIC_ARN=$SNS_TOPIC_ARN"
echo "SQS_QUEUE_URL=$SQS_QUEUE_URL"
echo "SQS_DLQ_URL=$SQS_DLQ_URL"
echo "ECR_REPOSITORY_URL=$ECR_REPOSITORY_URL"
echo "LAMBDA_FUNCTION_NAME=$LAMBDA_FUNCTION_NAME"

# Instructions to add to .env file
echo -e "\nAdd these to your .env file:"
cat << EOF > ../.env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=eu-west-2
SNS_TOPIC_ARN=$SNS_TOPIC_ARN
SQS_QUEUE_URL=$SQS_QUEUE_URL
SQS_DLQ_URL=$SQS_DLQ_URL
EOF

echo "Created/updated ../.env file with the new values"
```

## Using the Lambda Function

The deployed Lambda function provides a REST API for managing newsletter subscriptions. Here's how to interact with it:

### API Endpoints

All endpoints are available at the base URL: `${BASE_URL}`

#### Health Check
```bash
curl "${BASE_URL}/healthz"
```
**Response**: `{"status": "healthy"}`

#### Subscribe an Email
```bash
curl -X POST "${BASE_URL}/subscriptions/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```
**Response**: `{"success": true, "message": "Confirmation email sent. Please check your inbox.", "subscription_arn": "..."}`

#### Unsubscribe an Email
```bash
curl -X POST "${BASE_URL}/subscriptions/unsubscribe" \
  -H "Content-Type: application/json" \
  -d '{"subscription_arn": "arn:aws:sns:..."}'
```
**Response**: `{"success": true, "message": "Successfully unsubscribed"}`

#### Check Subscription Status
```bash
curl "${BASE_URL}/subscriptions/user@example.com"
```
**Response**: `{"email": "user@example.com", "subscription_arn": "...", "status": "subscribed"}`

#### Get All Confirmed Subscriptions
```bash
curl "${BASE_URL}/subscriptions"
```
**Response**: `{"subscriptions": [{"email": "...", "subscription_arn": "...", "status": "subscribed"}, ...]}`

### Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid email format or SNS operation failed)
- `404` - Subscription not found
- `500` - Internal server error

### Example Workflow

```bash
# 1. Check if the service is healthy
curl "${BASE_URL}/healthz"

# 2. Subscribe a new user (will receive confirmation email)
curl -X POST "${BASE_URL}/subscriptions/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"email": "john.doe@example.com"}'

# 3. User clicks confirmation link in email...

# 4. Verify subscription status
curl "${BASE_URL}/subscriptions/john.doe@example.com"

# 5. Get all confirmed subscribers
curl "${BASE_URL}/subscriptions"

# 6. Unsubscribe (if needed)
curl -X POST "${BASE_URL}/subscriptions/unsubscribe" \
  -H "Content-Type: application/json" \
  -d '{"subscription_arn": "..."}'
```

### Integration Examples

#### JavaScript/Node.js
```javascript
const BASE_URL = 'https://your-api-gateway-url.amazonaws.com';

// Subscribe
const subscribe = async (email) => {
  const response = await fetch(`${BASE_URL}/subscriptions/subscribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  return response.json();
};

// Check status
const checkStatus = async (email) => {
  const response = await fetch(`${BASE_URL}/subscriptions/${email}`);
  return response.json();
};
```

#### Python
```python
import requests

BASE_URL = 'https://your-api-gateway-url.amazonaws.com'

# Subscribe
def subscribe(email):
    response = requests.post(
        f"{BASE_URL}/subscriptions/subscribe",
        json={"email": email}
    )
    return response.json()

# Check status
def check_status(email):
    response = requests.get(f"{BASE_URL}/subscriptions/{email}")
    return response.json()
```

### Monitoring & Alerts

The infrastructure includes CloudWatch alarms that trigger SNS notifications for:
- Subscription errors (messages in DLQ)
- High subscription rates (spikes)
- Failed SNS operations

Check your email for these notifications.

## Update

```bash
IMAGE_TAG=v2
docker buildx build --platform linux/amd64 --load -t ${ECR_URL}:${IMAGE_TAG} .

# auth 
aws ecr get-login-password --region eu-west-2 \
 | docker login --username AWS --password-stdin $(echo $ECR_URL | cut -d'/' -f1)

# push
docker push ${ECR_URL}:${IMAGE_TAG}
cd infra && terraform apply -auto-approve -var="image_tag=${IMAGE_TAG}"
```

## Architecture Benefits

1. **Double Opt-in**: SNS handles confirmation emails automatically
2. **Compliance**: Built-in unsubscribe management helps with GDPR and CAN-SPAM
3. **Scalability**: AWS manages the infrastructure
4. **Reliability**: SQS provides message persistence and retry logic
5. **Monitoring**: CloudWatch metrics for subscription activities
6. **Cost-effective**: Pay only for what you use

## Notes

- Region, names, and retention live in `infra/variables.tf`
- CORS is configured for `https://fastaiconsulting-net.github.io`
- The confirmation email template can be customized via the AWS Console
- Users can unsubscribe directly from email links or via the API