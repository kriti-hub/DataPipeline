#!/usr/bin/env bash
# ============================================================================
# Deploy all BigQuery views for Looker Studio dashboard.
# Usage: bash sql/views/deploy_views.sh
# Requires: gcloud CLI authenticated with BigQuery access
# ============================================================================

set -euo pipefail

# Load environment
if [ -f .env ]; then
  set -a; source .env; set +a
fi

PROJECT="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID in .env}"
DATASET="people_analytics"
VIEWS_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Deploying BigQuery views to ${PROJECT}.${DATASET} ==="

for sql_file in "${VIEWS_DIR}"/v_*.sql; do
  view_name=$(basename "$sql_file" .sql)
  echo "  Creating view: ${view_name}..."
  bq query \
    --project_id="${PROJECT}" \
    --use_legacy_sql=false \
    --nouse_cache \
    < "$sql_file"
  echo "  Done: ${view_name}"
done

echo ""
echo "=== All views deployed. Verify with: ==="
echo "  bq ls --project_id=${PROJECT} ${DATASET}"
echo ""
echo "Views available for Looker Studio:"
echo "  - v_kpi_summary"
echo "  - v_staffing_coverage_by_location"
echo "  - v_shift_gap_heatmap"
echo "  - v_labor_cost_monthly_trend"
echo "  - v_overtime_hotspots"
echo "  - v_pipeline_health"
echo "  - v_dq_scorecard"
