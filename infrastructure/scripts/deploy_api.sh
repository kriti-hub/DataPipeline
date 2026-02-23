#!/usr/bin/env bash
# =============================================================================
# WellNow Staffing Analytics — Deploy HRIS API to Cloud Run
# =============================================================================
set -euo pipefail

if [ -f .env ]; then
  set -a; source .env; set +a
fi

PROJECT_ID="${GCP_PROJECT_ID:?'GCP_PROJECT_ID not set'}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${CLOUD_RUN_SERVICE_NAME:-wellnow-hris-api}"
MAX_INSTANCES="${CLOUD_RUN_MAX_INSTANCES:-1}"

echo "=== Deploying HRIS API to Cloud Run ==="

# Build and deploy from src/api/
cd src/api

gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --max-instances "${MAX_INSTANCES}" \
  --memory 256Mi \
  --cpu 1 \
  --timeout 60 \
  --set-env-vars "HRIS_API_KEY=${HRIS_API_KEY}" \
  --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region "${REGION}" \
  --format 'value(status.url)')

echo "=== API deployed at: ${SERVICE_URL} ==="
echo "Test with: curl -H 'X-API-Key: ${HRIS_API_KEY}' ${SERVICE_URL}/health"
