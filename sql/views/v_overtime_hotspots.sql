-- ============================================================================
-- View:        people_analytics.v_overtime_hotspots
-- Description: Top overtime locations with cumulative cost impact for
--              the Looker Studio waterfall / Pareto chart.
-- ============================================================================

CREATE OR REPLACE VIEW `people_analytics.v_overtime_hotspots` AS
WITH location_ot AS (
  SELECT
    dl.location_key,
    dl.location_name,
    dl.region,
    dl.location_type,
    ROUND(SUM(fs.overtime_hours), 1)         AS total_overtime_hours,
    ROUND(SUM(fs.overtime_hours) * 75, 0)    AS estimated_ot_cost,
    ROUND(AVG(fs.labor_cost_per_visit), 2)   AS avg_cost_per_visit
  FROM `people_analytics.fact_daily_staffing` fs
  JOIN `people_analytics.dim_location` dl
    ON fs.location_key = dl.location_key
  GROUP BY dl.location_key, dl.location_name, dl.region, dl.location_type
  HAVING SUM(fs.overtime_hours) > 0
)
SELECT
  *,
  SUM(estimated_ot_cost) OVER (
    ORDER BY total_overtime_hours DESC
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_ot_cost,
  ROUND(
    SUM(estimated_ot_cost) OVER (
      ORDER BY total_overtime_hours DESC
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) * 100.0 / SUM(estimated_ot_cost) OVER (), 1
  ) AS cumulative_pct
FROM location_ot
ORDER BY total_overtime_hours DESC;
