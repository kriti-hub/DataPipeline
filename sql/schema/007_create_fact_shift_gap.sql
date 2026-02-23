-- ============================================================================
-- File:        007_create_fact_shift_gap.sql
-- Description: Creates the fact_shift_gap fact table.
--              Stores shift-level understaffing and overstaffing detection
--              data per location. Each row represents one shift window
--              (AM/PM/Evening) at one location on one day. Partitioned by
--              snapshot_date and clustered by location and shift window.
-- Table:       people_analytics.fact_shift_gap
-- ============================================================================

CREATE TABLE IF NOT EXISTS people_analytics.fact_shift_gap (
  date_key              INT64 NOT NULL,
  snapshot_date         DATE NOT NULL,
  location_key          INT64 NOT NULL,
  shift_window          STRING NOT NULL,     -- AM (8-12), PM (12-16), Evening (16-20)
  required_providers    INT64,
  scheduled_providers   INT64,
  actual_providers      INT64,
  gap_flag              BOOL,                -- TRUE when actual < required
  excess_flag           BOOL,                -- TRUE when actual > required * 1.15
  gap_hours             FLOAT64,             -- Hours of unfilled provider time
  excess_hours          FLOAT64,             -- Hours of excess provider time
  _loaded_at            TIMESTAMP NOT NULL,
  _batch_id             STRING
)
PARTITION BY snapshot_date
CLUSTER BY location_key, shift_window;
