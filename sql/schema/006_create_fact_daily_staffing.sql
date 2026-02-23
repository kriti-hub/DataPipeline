-- ============================================================================
-- File:        006_create_fact_daily_staffing.sql
-- Description: Creates the fact_daily_staffing fact table.
--              Stores daily staffing metrics per location including provider
--              hours, support staff hours, patient visits, coverage scores,
--              and labor cost figures. Partitioned by snapshot_date for
--              efficient time-range queries and cost control.
-- Table:       people_analytics.fact_daily_staffing
-- ============================================================================

CREATE TABLE IF NOT EXISTS people_analytics.fact_daily_staffing (
  date_key                    INT64 NOT NULL,
  snapshot_date               DATE NOT NULL,
  location_key                INT64 NOT NULL,
  -- Provider staffing
  scheduled_provider_hours    FLOAT64,
  actual_provider_hours       FLOAT64,
  required_provider_hours     FLOAT64,       -- Based on patient demand model
  -- Support staff
  scheduled_support_hours     FLOAT64,
  actual_support_hours        FLOAT64,
  -- Operational
  overtime_hours              FLOAT64,
  callout_count               INT64,
  -- Patient volume
  patient_visits              INT64,
  -- Derived metrics (computed in transform)
  patients_per_provider_hour  FLOAT64,
  avg_wait_time_minutes       FLOAT64,
  coverage_score              FLOAT64,       -- actual / required
  labor_cost_total            FLOAT64,
  labor_cost_per_visit        FLOAT64,
  -- Metadata
  _loaded_at                  TIMESTAMP NOT NULL,
  _batch_id                   STRING
)
PARTITION BY snapshot_date
CLUSTER BY location_key;
