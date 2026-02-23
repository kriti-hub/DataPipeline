#!/usr/bin/env bash
# =============================================================================
# WellNow Staffing Analytics — Deploy ETL Pipeline to Cloud Functions
# =============================================================================
# Builds a staging directory with the correct layout for Cloud Functions 2nd
# gen, then deploys.  The staging dir contains:
#   main.py              ← thin entry-point that imports from src.etl
#   src/                 ← full src package (api is excluded to save space)
#   config/              ← quality_rules.yaml
#   requirements.txt     ← ETL dependencies
# =============================================================================
set -euo pipefail

if [ -f .env ]; then
  set -a; source .env; set +a
fi

PROJECT_ID="${GCP_PROJECT_ID:?'GCP_PROJECT_ID not set'}"
REGION="${GCP_REGION:-us-central1}"
FUNCTION_NAME="${CLOUD_FUNCTION_NAME:-wellnow-etl-pipeline}"
TIMEOUT="${CLOUD_FUNCTION_TIMEOUT:-540}"
MEMORY="${CLOUD_FUNCTION_MEMORY:-512MB}"

echo "=== Building staging directory for Cloud Functions ==="

STAGE_DIR=$(mktemp -d)
trap "rm -rf ${STAGE_DIR}" EXIT

# Copy the src/etl package (preserving package structure)
mkdir -p "${STAGE_DIR}/src"
cp src/__init__.py "${STAGE_DIR}/src/"
cp -r src/etl "${STAGE_DIR}/src/etl"

# Remove test files and __pycache__ to reduce deploy size
rm -rf "${STAGE_DIR}/src/etl/tests"
find "${STAGE_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Copy config directory (quality_rules.yaml)
mkdir -p "${STAGE_DIR}/config"
cp config/quality_rules.yaml "${STAGE_DIR}/config/"

# Copy ETL requirements.txt
cp src/etl/requirements.txt "${STAGE_DIR}/requirements.txt"

# Create the thin Cloud Functions entry-point at the staging root
cat > "${STAGE_DIR}/main.py" << 'PYEOF'
"""Cloud Function entry point — delegates to the ETL pipeline."""
from src.etl.main import main  # noqa: F401 — re-export for GCF
PYEOF

echo "Staging directory ready: ${STAGE_DIR}"
ls -la "${STAGE_DIR}"

echo ""
echo "=== Deploying ETL Pipeline to Cloud Functions ==="

gcloud functions deploy "${FUNCTION_NAME}" \
  --gen2 \
  --runtime python311 \
  --region "${REGION}" \
  --source "${STAGE_DIR}" \
  --entry-point main \
  --trigger-http \
  --allow-unauthenticated \
  --timeout "${TIMEOUT}" \
  --memory "${MEMORY}" \
  --set-env-vars "LOCAL_MODE=false,GCP_PROJECT_ID=${PROJECT_ID},BQ_DATASET_ID=${BQ_DATASET_ID:-people_analytics},HRIS_API_URL=${HRIS_API_URL},HRIS_API_KEY=${HRIS_API_KEY},GCS_STAGING_BUCKET=${GCS_STAGING_BUCKET},GCS_DASHBOARD_BUCKET=${GCS_DASHBOARD_BUCKET}" \
  --quiet

FUNCTION_URL=$(gcloud functions describe "${FUNCTION_NAME}" \
  --gen2 \
  --region "${REGION}" \
  --format 'value(serviceConfig.uri)')

echo "=== ETL deployed at: ${FUNCTION_URL} ==="
echo "Trigger with: curl ${FUNCTION_URL}"
