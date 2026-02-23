-- ============================================================================
-- File:        003_create_dim_location.sql
-- Description: Creates the dim_location dimension table.
--              Stores WellNow clinic location master data including region,
--              operating hours, and budgeted FTE targets for staffing analysis.
-- Table:       people_analytics.dim_location
-- ============================================================================

CREATE TABLE IF NOT EXISTS people_analytics.dim_location (
  location_key            INT64 NOT NULL,
  location_id             STRING NOT NULL,      -- LOC-XXX
  location_name           STRING NOT NULL,
  region                  STRING NOT NULL,
  state                   STRING NOT NULL,
  metro_area              STRING,
  location_type           STRING NOT NULL,       -- Urban, Suburban, Rural
  operating_hours_start   STRING,                -- e.g., '08:00'
  operating_hours_end     STRING,                -- e.g., '20:00'
  days_open_per_week      INT64,
  budgeted_provider_fte   FLOAT64,
  budgeted_support_fte    FLOAT64,
  opened_date             DATE,
  is_active               BOOL DEFAULT TRUE,
  _loaded_at              TIMESTAMP NOT NULL
)
CLUSTER BY region, state;
