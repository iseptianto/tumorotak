#!/bin/bash

# Deploy to Google Cloud Run
# Usage: ./deploy-cloudrun.sh [PROJECT_ID] [REGION]

set -e

PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"asia-southeast2"}
SERVICE_NAME="tumorotak"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying to Google Cloud Run..."
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Build and push image
echo "📦 Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

echo "⬆️  Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8080 \
  --project ${PROJECT_ID}

echo ""
echo "✅ Deployment complete!"
echo "🔗 Service URL:"
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)' --project ${PROJECT_ID}
