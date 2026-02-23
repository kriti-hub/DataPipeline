-- ============================================================================
-- File:        008_create_utility_tables.sql
-- Description: Creates the utility/metadata tables for pipeline observability.
--              _pipeline_runs tracks ETL execution history and performance.
--              _data_quality_log stores results from all 15 DQ validation rules.
-- Tables:      people_analytics._pipeline_runs
--              people_analytics._data_quality_log
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Pipeline Run Tracking
-- Records one row per ETL pipeline execution with timing, record counts,
-- and success/failure status for operational monitoring.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS people_analytics._pipeline_runs (
  run_id                STRING NOT NULL,
  pipeline_name         STRING NOT NULL,
  started_at            TIMESTAMP NOT NULL,
  completed_at          TIMESTAMP,
  status                STRING,             -- Success, Failed, Partial
  records_extracted     INT64,
  records_validated     INT64,
  records_quarantined   INT64,
  records_loaded        INT64,
  error_message         STRING,
  run_duration_seconds  FLOAT64,
  _batch_id             STRING
);

-- -----------------------------------------------------------------------------
-- Data Quality Log
-- Records the result of each DQ validation rule per pipeline run.
-- Used by the Data Quality Monitor dashboard page and for trend analysis.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS people_analytics._data_quality_log (
  check_date        DATE NOT NULL,
  check_name        STRING NOT NULL,
  table_name        STRING NOT NULL,
  check_type        STRING NOT NULL,
  records_checked   INT64,
  records_passed    INT64,
  records_failed    INT64,
  pass_rate         FLOAT64,
  severity          STRING NOT NULL,    -- Critical, High, Medium, Low
  status            STRING NOT NULL,    -- Pass, Warn, Fail
  details           STRING,
  _batch_id         STRING
);
