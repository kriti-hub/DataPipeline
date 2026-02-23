#!/usr/bin/env bash
# =============================================================================
# WellNow Staffing Analytics — BigQuery Schema Setup
# =============================================================================
# Runs all SQL schema files in order to create the data warehouse.
# =============================================================================
set -euo pipefail

if [ -f .env ]; then
  set -a; source .env; set +a
fi

PROJECT_ID="${GCP_PROJECT_ID:?'GCP_PROJECT_ID not set'}"

echo "=== Setting up BigQuery schema ==="

# Run schema files in order
for sql_file in sql/schema/0*.sql; do
  echo "Running: ${sql_file}"
  bq query --use_legacy_sql=false --project_id="${PROJECT_ID}" < "${sql_file}"
done

echo "=== Seeding dim_date ==="
bq query --use_legacy_sql=false --project_id="${PROJECT_ID}" < sql/seed/seed_dim_date.sql

echo "=== BigQuery schema setup complete ==="
echo "Verify with: bq ls ${PROJECT_ID}:people_analytics"
