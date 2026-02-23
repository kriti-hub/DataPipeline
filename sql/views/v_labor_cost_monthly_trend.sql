-- ============================================================================
-- View:        people_analytics.v_labor_cost_monthly_trend
-- Description: Monthly labor cost per visit trend line for Looker Studio.
--              Aggregates daily staffing data by month with regional breakdown.
-- ============================================================================

CREATE OR REPLACE VIEW `people_analytics.v_labor_cost_monthly_trend` AS
SELECT
  FORMAT_DATE('%Y-%m', fs.snapshot_date)   AS month,
  dl.region,
  ROUND(SUM(fs.labor_cost_total), 0)      AS total_labor_cost,
  SUM(fs.patient_visits)                   AS total_visits,
  ROUND(SUM(fs.labor_cost_total) / NULLIF(SUM(fs.patient_visits), 0), 2) AS cost_per_visit,
  ROUND(SUM(fs.overtime_hours), 1)         AS total_overtime_hours,
  COUNT(DISTINCT fs.location_key)          AS locations_reporting
FROM `people_analytics.fact_daily_staffing` fs
JOIN `people_analytics.dim_location` dl
  ON fs.location_key = dl.location_key
GROUP BY month, dl.region
ORDER BY month, dl.region;
