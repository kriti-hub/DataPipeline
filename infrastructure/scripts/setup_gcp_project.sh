#!/usr/bin/env bash
# =============================================================================
# WellNow Staffing Analytics — GCP Project Setup
# =============================================================================
# Run once to configure the GCP project for this POC.
# Prerequisites: gcloud CLI installed and authenticated.
# =============================================================================
set -euo pipefail

# Load environment variables
if [ -f .env ]; then
  set -a; source .env; set +a
fi

PROJECT_ID="${GCP_PROJECT_ID:?'GCP_PROJECT_ID not set'}"
REGION="${GCP_REGION:-us-central1}"

echo "=== Setting up GCP project: ${PROJECT_ID} ==="

# Set active project
gcloud config set project "${PROJECT_ID}"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
  bigquery.googleapis.com \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com

# Create staging bucket
echo "Creating Cloud Storage buckets..."
gsutil mb -l "${REGION}" "gs://${GCS_STAGING_BUCKET}" 2>/dev/null || echo "Staging bucket already exists"
gsutil mb -l "${REGION}" "gs://${GCS_DASHBOARD_BUCKET}" 2>/dev/null || echo "Dashboard bucket already exists"

# Set up billing alert
echo "Setting up billing alert at \$5..."
gcloud billing budgets create \
  --billing-account="$(gcloud billing accounts list --format='value(name)' --limit=1)" \
  --display-name="WellNow POC Budget Alert" \
  --budget-amount=5.00USD \
  --threshold-rule=percent=0.50 \
  --threshold-rule=percent=0.90 \
  --threshold-rule=percent=1.00 \
  2>/dev/null || echo "Budget alert may already exist or billing account not linked"

echo "=== GCP project setup complete ==="
