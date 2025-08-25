# Younews News Agent

Younews runs daily on AWS trigger by a cron job.

## Deployment

#### Manual

Run manually by navigating to the project root directory and running:

```
./daily-deploy.sh
```

#### AWS 

1. Update config.yaml to save to a `tmp/reports`.

2. Build, tag and push to ECR.

```sh
export IMG_NAME="younews-engine"
export IMG_VERSION="0.0.1"
export AWS_REGION="eu-west-2"
export AWS_ACCOUNT="084285615195"

# Build the Docker image
docker build -t ${IMG_NAME}:${IMG_VERSION} .

# Create ECR repo (once)
aws ecr create-repository --repository-name ${IMG_NAME} --region ${AWS_REGION}

# authenicate ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Tag for ECR
docker tag ${IMG_NAME}:${IMG_VERSION} ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMG_NAME}:${IMG_VERSION}

# Push to ECR
docker push ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMG_NAME}:${IMG_VERSION}
```