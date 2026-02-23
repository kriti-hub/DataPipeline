#!/usr/bin/env bash
# =============================================================================
# WellNow Staffing Analytics — Full Teardown
# =============================================================================
# Removes all GCP resources created by this POC.
# WARNING: This is destructive and irreversible!
# =============================================================================
set -euo pipefail

if [ -f .env ]; then
  set -a; source .env; set +a
fi

PROJECT_ID="${GCP_PROJECT_ID:?'GCP_PROJECT_ID not set'}"
REGION="${GCP_REGION:-us-central1}"

echo "========================================="
echo "  WARNING: This will delete ALL resources"
echo "========================================="
read -p "Type 'yes' to confirm: " confirm
if [ "${confirm}" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

echo "=== Deleting Cloud Scheduler job ==="
gcloud scheduler jobs delete "wellnow-etl-daily" \
  --location "${REGION}" --quiet 2>/dev/null || echo "Scheduler job not found"

echo "=== Deleting Cloud Function ==="
gcloud functions delete "${CLOUD_FUNCTION_NAME:-wellnow-etl-pipeline}" \
  --gen2 --region "${REGION}" --quiet 2>/dev/null || echo "Cloud Function not found"

echo "=== Deleting Cloud Run service ==="
gcloud run services delete "${CLOUD_RUN_SERVICE_NAME:-wellnow-hris-api}" \
  --region "${REGION}" --quiet 2>/dev/null || echo "Cloud Run service not found"

echo "=== Deleting BigQuery dataset ==="
bq rm -r -f "${PROJECT_ID}:people_analytics" 2>/dev/null || echo "Dataset not found"

echo "=== Deleting Cloud Storage buckets ==="
gsutil rm -r "gs://${GCS_STAGING_BUCKET}" 2>/dev/null || echo "Staging bucket not found"
gsutil rm -r "gs://${GCS_DASHBOARD_BUCKET}" 2>/dev/null || echo "Dashboard bucket not found"

echo "=== Deleting secrets ==="
gcloud secrets delete "hris-api-key" --quiet 2>/dev/null || echo "Secret not found"

echo "=== Teardown complete ==="
