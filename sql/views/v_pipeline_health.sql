-- ============================================================================
-- View:        people_analytics.v_pipeline_health
-- Description: Pipeline run history and data quality scores for the
--              Looker Studio Data Quality Monitor page.
-- ============================================================================

CREATE OR REPLACE VIEW `people_analytics.v_pipeline_health` AS
SELECT
  run_id,
  pipeline_name,
  started_at,
  completed_at,
  status,
  records_extracted,
  records_validated,
  records_quarantined,
  records_loaded,
  run_duration_seconds,
  error_message,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), completed_at, HOUR) AS hours_since_last_run,
  CASE
    WHEN TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), completed_at, HOUR) <= 24 THEN 'Fresh'
    WHEN TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), completed_at, HOUR) <= 48 THEN 'Stale'
    ELSE 'Critical'
  END AS freshness_status
FROM `people_analytics._pipeline_runs`
ORDER BY started_at DESC;
