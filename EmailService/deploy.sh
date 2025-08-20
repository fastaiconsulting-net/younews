IMAGE_TAG=v0.0.2
echo "🏷️ Using image tag: ${IMAGE_TAG}"

cd infra
echo "📂 Changed to infra directory"

ECR_URL=$(terraform output -raw ecr_repository_url)
echo "📦 Got ECR URL: ${ECR_URL}"

cd ..
echo "📂 Changed back to root directory"

echo "🔨 Building Docker image..."
docker buildx build --platform linux/amd64 --load -t ${ECR_URL}:${IMAGE_TAG} .
echo "✅ Docker build complete"

echo "🔑 Authenticating with ECR..."
# auth 
aws ecr get-login-password --region eu-west-2 \
 | docker login --username AWS --password-stdin $(echo $ECR_URL | cut -d'/' -f1)
echo "✅ ECR authentication complete"

echo "⬆️ Pushing image to ECR..."
# push
docker push ${ECR_URL}:${IMAGE_TAG}
echo "✅ Image push complete"

echo "🚀 Applying Terraform changes..."
cd infra && terraform apply -target=aws_lambda_function.api -auto-approve -var="image_tag=${IMAGE_TAG}"
echo "✅ Terraform apply complete"
