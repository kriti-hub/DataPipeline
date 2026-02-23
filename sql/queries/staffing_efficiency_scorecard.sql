-- ============================================================================
-- File:        staffing_efficiency_scorecard.sql
-- Description: Location Staffing Efficiency Scorecard.
--              Aggregates 90-day staffing metrics per location with weekly
--              granularity, computes coverage trends using window functions,
--              and classifies each location's staffing health using CASE
--              logic (Chronically Understaffed / Needs Attention /
--              Optimally Staffed / Potentially Overstaffed).
-- Query:       Showcase Query 1 from the PRD
-- Tables:      people_analytics.fact_daily_staffing
--              people_analytics.dim_location
-- ============================================================================

WITH location_metrics AS (
  SELECT
    l.location_name,
    l.region,
    l.state,
    l.location_type,
    DATE_TRUNC(ds.snapshot_date, WEEK(MONDAY)) AS week_start,
    AVG(ds.coverage_score) AS avg_coverage,
    SUM(ds.overtime_hours) AS total_overtime,
    AVG(ds.patients_per_provider_hour) AS avg_productivity,
    AVG(ds.avg_wait_time_minutes) AS avg_wait_time,
    SUM(ds.labor_cost_total) AS total_labor_cost,
    SUM(ds.patient_visits) AS total_visits,
    SAFE_DIVIDE(SUM(ds.labor_cost_total), NULLIF(SUM(ds.patient_visits), 0)) AS cost_per_visit
  FROM people_analytics.fact_daily_staffing ds
  JOIN people_analytics.dim_location l ON ds.location_key = l.location_key
  WHERE ds.snapshot_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY 1, 2, 3, 4, 5
),
location_summary AS (
  SELECT
    location_name,
    region,
    state,
    location_type,
    ROUND(AVG(avg_coverage), 3) AS avg_coverage_score,
    ROUND(AVG(avg_productivity), 2) AS avg_patients_per_provider_hr,
    ROUND(AVG(avg_wait_time), 1) AS avg_wait_minutes,
    ROUND(AVG(cost_per_visit), 2) AS avg_cost_per_visit,
    ROUND(SUM(total_overtime), 1) AS total_overtime_hours_90d,
    ROUND(SUM(total_visits), 0) AS total_visits_90d,
    ROUND(AVG(avg_coverage) - LAG(AVG(avg_coverage), 1) OVER (
      PARTITION BY location_name ORDER BY MAX(week_start)
    ), 3) AS coverage_trend_wow
  FROM location_metrics
  GROUP BY location_name, region, state, location_type
)
SELECT
  *,
  CASE
    WHEN avg_coverage_score < 0.85 THEN 'Chronically Understaffed'
    WHEN avg_coverage_score BETWEEN 0.85 AND 0.95 THEN 'Needs Attention'
    WHEN avg_coverage_score BETWEEN 0.95 AND 1.10 THEN 'Optimally Staffed'
    WHEN avg_coverage_score > 1.10 THEN 'Potentially Overstaffed'
  END AS staffing_classification,
  CASE
    WHEN coverage_trend_wow > 0.02 THEN 'Improving'
    WHEN coverage_trend_wow < -0.02 THEN 'Declining'
    ELSE 'Stable'
  END AS trend_direction
FROM location_summary
ORDER BY avg_coverage_score ASC;
