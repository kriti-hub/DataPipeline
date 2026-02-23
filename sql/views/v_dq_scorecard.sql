-- ============================================================================
-- View:        people_analytics.v_dq_scorecard
-- Description: Data quality scorecard by severity level with weighted overall
--              score for the Looker Studio Data Quality page.
-- ============================================================================

CREATE OR REPLACE VIEW `people_analytics.v_dq_scorecard` AS
WITH latest_run AS (
  SELECT _batch_id
  FROM `people_analytics._data_quality_log`
  ORDER BY check_date DESC
  LIMIT 1
),
severity_scores AS (
  SELECT
    dq.severity,
    COUNT(*)                                          AS total_checks,
    ROUND(AVG(dq.pass_rate), 3)                       AS avg_pass_rate,
    COUNTIF(dq.status = 'Pass')                       AS checks_passed,
    COUNTIF(dq.status = 'Fail')                       AS checks_failed,
    COUNTIF(dq.status = 'Warn')                       AS checks_warned
  FROM `people_analytics._data_quality_log` dq
  WHERE dq._batch_id = (SELECT _batch_id FROM latest_run)
  GROUP BY dq.severity
)
SELECT
  severity,
  total_checks,
  avg_pass_rate,
  checks_passed,
  checks_failed,
  checks_warned,
  CASE severity
    WHEN 'Critical' THEN 0.40
    WHEN 'High'     THEN 0.30
    WHEN 'Medium'   THEN 0.20
    WHEN 'Low'      THEN 0.10
  END AS severity_weight
FROM severity_scores
ORDER BY
  CASE severity
    WHEN 'Critical' THEN 1
    WHEN 'High'     THEN 2
    WHEN 'Medium'   THEN 3
    WHEN 'Low'      THEN 4
  END;
