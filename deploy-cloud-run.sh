#!/bin/bash
# Run following commands to deploy
# chmod +x deploy-cloud-run.sh (first time needed to give executable permissions)
# ./deploy-cloud-run.sh

# Load environment variables from .env file
set -o allexport
source .env
set +o allexport

# Full image path
FULL_IMAGE_NAME="gcr.io/$PROJECT_ID/$IMAGE_NAME"

# Build and push the Docker image
docker buildx build --platform linux/amd64 -t $FULL_IMAGE_NAME --push .

# Deploy to Cloud Run with environment variables, secret, and volume mounts
gcloud run deploy $SERVICE_NAME \
  --image $FULL_IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars FLASK_SECRET_KEY="$FLASK_SECRET_KEY" \
  --set-env-vars APP_ENV="production" \
  --set-env-vars GOOGLE_CLOUD_PROJECT_ID="$GOOGLE_CLOUD_PROJECT_ID" \
  --set-env-vars FIRESTORE_COLLECTION_NAME="$FIRESTORE_COLLECTION_NAME" \
  --set-env-vars FIREBASE_STORAGE_BUCKET="$FIREBASE_STORAGE_BUCKET" \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS="$SECRET_PATH" \
  --update-secrets $SECRET_PATH=$SECRET_NAME:latest





