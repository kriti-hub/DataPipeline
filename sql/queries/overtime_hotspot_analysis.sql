-- ============================================================================
-- File:        overtime_hotspot_analysis.sql
-- Description: Overtime Hotspot Analysis and Labor Cost Impact.
--              Aggregates monthly overtime hours and labor cost by location,
--              computes regional benchmarks using window functions, calculates
--              rolling 3-month overtime totals, and classifies locations by
--              overtime alert level relative to their regional average.
-- Query:       Showcase Query 3 from the PRD
-- Tables:      people_analytics.fact_daily_staffing
--              people_analytics.dim_location
-- ============================================================================

WITH overtime_by_location AS (
  SELECT
    l.location_name,
    l.region,
    DATE_TRUNC(ds.snapshot_date, MONTH) AS month,
    SUM(ds.overtime_hours) AS monthly_overtime_hours,
    SUM(ds.labor_cost_total) AS monthly_labor_cost,
    SUM(ds.patient_visits) AS monthly_visits,
    ROUND(SAFE_DIVIDE(SUM(ds.overtime_hours),
      SUM(ds.actual_provider_hours + ds.actual_support_hours)), 3) AS overtime_rate,
    ROUND(SAFE_DIVIDE(SUM(ds.labor_cost_total),
      NULLIF(SUM(ds.patient_visits), 0)), 2) AS cost_per_visit
  FROM people_analytics.fact_daily_staffing ds
  JOIN people_analytics.dim_location l ON ds.location_key = l.location_key
  GROUP BY 1, 2, 3
),
with_benchmarks AS (
  SELECT
    *,
    AVG(overtime_rate) OVER (PARTITION BY region, month) AS regional_avg_ot_rate,
    AVG(cost_per_visit) OVER (PARTITION BY region, month) AS regional_avg_cpv,
    SUM(monthly_overtime_hours) OVER (
      PARTITION BY location_name ORDER BY month
      ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_3m_overtime
  FROM overtime_by_location
)
SELECT
  location_name,
  region,
  month,
  monthly_overtime_hours,
  overtime_rate,
  regional_avg_ot_rate,
  ROUND(overtime_rate - regional_avg_ot_rate, 3) AS ot_rate_vs_regional_avg,
  cost_per_visit,
  regional_avg_cpv,
  rolling_3m_overtime,
  CASE
    WHEN overtime_rate > regional_avg_ot_rate * 1.5 THEN 'Critical -- Significantly Above Regional Avg'
    WHEN overtime_rate > regional_avg_ot_rate * 1.2 THEN 'Elevated -- Above Regional Avg'
    ELSE 'Normal'
  END AS overtime_alert_level
FROM with_benchmarks
WHERE month >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
ORDER BY overtime_rate DESC;
