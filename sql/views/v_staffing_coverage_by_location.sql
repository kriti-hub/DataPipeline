-- ============================================================================
-- View:        people_analytics.v_staffing_coverage_by_location
-- Description: Per-location staffing coverage summary for the coverage map
--              and location comparison charts in Looker Studio.
--              Joins fact_daily_staffing with dim_location for geography.
-- ============================================================================

CREATE OR REPLACE VIEW `people_analytics.v_staffing_coverage_by_location` AS
SELECT
  dl.location_key,
  dl.location_name,
  dl.region,
  dl.state,
  dl.metro_area,
  dl.location_type,
  ROUND(AVG(fs.coverage_score), 3)         AS avg_coverage,
  SUM(fs.patient_visits)                   AS total_visits,
  ROUND(AVG(fs.avg_wait_time_minutes), 1)  AS avg_wait_time,
  ROUND(SUM(fs.overtime_hours), 1)         AS total_overtime,
  ROUND(AVG(fs.labor_cost_per_visit), 2)   AS avg_cost_per_visit,
  ROUND(AVG(fs.patients_per_provider_hour), 1) AS avg_patients_per_provider_hr,
  COUNT(DISTINCT fs.snapshot_date)         AS days_measured
FROM `people_analytics.fact_daily_staffing` fs
JOIN `people_analytics.dim_location` dl
  ON fs.location_key = dl.location_key
GROUP BY
  dl.location_key, dl.location_name, dl.region,
  dl.state, dl.metro_area, dl.location_type;
