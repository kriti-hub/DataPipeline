-- ============================================================================
-- File:        shift_gap_float_deployment.sql
-- Description: Shift Gap Analysis with Float Clinician Deployment
--              Recommendations. Analyzes 30-day shift gap patterns by
--              location, shift window, and day of week. Uses DENSE_RANK
--              to prioritize locations within each region by gap frequency
--              and severity, then generates actionable deployment
--              recommendations for float/PRN clinicians.
-- Query:       Showcase Query 2 from the PRD
-- Tables:      people_analytics.fact_shift_gap
--              people_analytics.dim_location
-- ============================================================================

WITH gap_summary AS (
  SELECT
    l.region,
    l.location_name,
    l.location_id,
    sg.shift_window,
    EXTRACT(DAYOFWEEK FROM sg.snapshot_date) AS dow_num,
    FORMAT_DATE('%A', sg.snapshot_date) AS day_name,
    COUNT(*) AS total_shifts_observed,
    COUNTIF(sg.gap_flag) AS understaffed_shifts,
    COUNTIF(sg.excess_flag) AS overstaffed_shifts,
    ROUND(SUM(sg.gap_hours), 1) AS total_gap_hours,
    ROUND(SAFE_DIVIDE(COUNTIF(sg.gap_flag), COUNT(*)), 3) AS gap_frequency,
    ROUND(AVG(CASE WHEN sg.gap_flag THEN sg.gap_hours END), 1) AS avg_gap_when_short
  FROM people_analytics.fact_shift_gap sg
  JOIN people_analytics.dim_location l ON sg.location_key = l.location_key
  WHERE sg.snapshot_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY 1, 2, 3, 4, 5, 6
),
ranked_needs AS (
  SELECT
    *,
    DENSE_RANK() OVER (
      PARTITION BY region
      ORDER BY gap_frequency DESC, total_gap_hours DESC
    ) AS regional_priority
  FROM gap_summary
  WHERE gap_frequency >= 0.20
)
SELECT
  region,
  location_name,
  location_id,
  shift_window,
  day_name,
  gap_frequency AS pct_shifts_understaffed,
  total_gap_hours AS gap_hours_last_30d,
  avg_gap_when_short AS avg_gap_hrs_per_incident,
  regional_priority AS deploy_priority,
  CASE
    WHEN regional_priority <= 3 THEN 'URGENT -- Deploy Float Immediately'
    WHEN regional_priority <= 7 THEN 'HIGH -- Schedule Float Coverage'
    ELSE 'MONITOR -- Track for Escalation'
  END AS recommended_action
FROM ranked_needs
WHERE regional_priority <= 15
ORDER BY region, regional_priority;
