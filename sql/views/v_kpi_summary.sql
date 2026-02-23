-- ============================================================================
-- View:        people_analytics.v_kpi_summary
-- Description: Top-level KPI cards for the Looker Studio staffing dashboard.
--              Computes rolling 30-day aggregates for 6 key workforce metrics.
-- Refreshes:   Automatically on each query (uses live fact tables)
-- ============================================================================

CREATE OR REPLACE VIEW `people_analytics.v_kpi_summary` AS
WITH last_30 AS (
  SELECT *
  FROM `people_analytics.fact_daily_staffing`
  WHERE snapshot_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
)
SELECT
  ROUND(AVG(coverage_score), 3)                     AS avg_coverage_score,
  ROUND(SUM(overtime_hours), 1)                      AS total_overtime_hours_30d,
  ROUND(AVG(labor_cost_per_visit), 2)                AS avg_cost_per_visit,
  ROUND(
    (SELECT COUNTIF(gap_flag = TRUE) / COUNT(*)
     FROM `people_analytics.fact_shift_gap`
     WHERE snapshot_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    ), 3
  )                                                  AS shift_gap_rate,
  ROUND(AVG(avg_wait_time_minutes), 1)               AS avg_wait_time,
  SUM(patient_visits)                                AS total_patient_visits_30d
FROM last_30;
