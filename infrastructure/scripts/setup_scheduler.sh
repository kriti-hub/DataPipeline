#!/usr/bin/env bash
# =============================================================================
# WellNow Staffing Analytics — Setup Cloud Scheduler
# =============================================================================
# Creates a Cloud Scheduler job to trigger the ETL pipeline daily at 6AM UTC.
# =============================================================================
set -euo pipefail

if [ -f .env ]; then
  set -a; source .env; set +a
fi

PROJECT_ID="${GCP_PROJECT_ID:?'GCP_PROJECT_ID not set'}"
REGION="${GCP_REGION:-us-central1}"
FUNCTION_NAME="${CLOUD_FUNCTION_NAME:-wellnow-etl-pipeline}"
CRON="${SCHEDULER_CRON:-0 6 * * *}"
TIMEZONE="${SCHEDULER_TIMEZONE:-UTC}"

# Get the Cloud Function URL
FUNCTION_URL=$(gcloud functions describe "${FUNCTION_NAME}" \
  --gen2 \
  --region "${REGION}" \
  --format 'value(serviceConfig.uri)')

echo "=== Creating Cloud Scheduler job ==="

gcloud scheduler jobs create http "wellnow-etl-daily" \
  --location "${REGION}" \
  --schedule "${CRON}" \
  --time-zone "${TIMEZONE}" \
  --uri "${FUNCTION_URL}" \
  --http-method POST \
  --attempt-deadline 600s \
  --description "Daily ETL pipeline trigger for WellNow staffing analytics" \
  2>/dev/null || \
gcloud scheduler jobs update http "wellnow-etl-daily" \
  --location "${REGION}" \
  --schedule "${CRON}" \
  --time-zone "${TIMEZONE}" \
  --uri "${FUNCTION_URL}" \
  --http-method POST \
  --attempt-deadline 600s

echo "=== Scheduler configured: ${CRON} ${TIMEZONE} ==="
echo "Manual trigger: gcloud scheduler jobs run wellnow-etl-daily --location=${REGION}"
