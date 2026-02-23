#!/usr/bin/env bash
# =============================================================================
# WellNow Staffing Analytics — Secret Manager Setup
# =============================================================================
# Stores secrets in GCP Secret Manager for production use.
# For development, use .env file instead.
# =============================================================================
set -euo pipefail

if [ -f .env ]; then
  set -a; source .env; set +a
fi

PROJECT_ID="${GCP_PROJECT_ID:?'GCP_PROJECT_ID not set'}"

echo "=== Setting up Secret Manager ==="

# Create secrets (will skip if already exists)
create_secret() {
  local name="$1"
  local value="$2"
  echo "Creating secret: ${name}"
  echo -n "${value}" | gcloud secrets create "${name}" \
    --replication-policy="automatic" \
    --data-file=- \
    2>/dev/null || \
  echo -n "${value}" | gcloud secrets versions add "${name}" --data-file=-
}

create_secret "hris-api-key" "${HRIS_API_KEY}"

echo "=== Secrets configured ==="
echo "Access in code: gcloud secrets versions access latest --secret=hris-api-key"
