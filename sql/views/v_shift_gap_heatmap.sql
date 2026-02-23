-- ============================================================================
-- View:        people_analytics.v_shift_gap_heatmap
-- Description: Location x Day-of-Week understaffing heatmap for Looker Studio.
--              Aggregates shift gap data by location and day of week to show
--              chronic understaffing patterns.
-- ============================================================================

CREATE OR REPLACE VIEW `people_analytics.v_shift_gap_heatmap` AS
SELECT
  dl.location_key,
  dl.location_name,
  dl.region,
  dl.location_type,
  EXTRACT(DAYOFWEEK FROM fg.snapshot_date) AS day_of_week,
  FORMAT_DATE('%A', fg.snapshot_date)       AS day_name,
  COUNT(*)                                 AS total_shifts,
  COUNTIF(fg.gap_flag = TRUE)              AS understaffed_shifts,
  ROUND(COUNTIF(fg.gap_flag = TRUE) / COUNT(*), 3) AS gap_frequency,
  ROUND(SUM(fg.gap_hours), 1)             AS total_gap_hours
FROM `people_analytics.fact_shift_gap` fg
JOIN `people_analytics.dim_location` dl
  ON fg.location_key = dl.location_key
GROUP BY
  dl.location_key, dl.location_name, dl.region,
  dl.location_type, day_of_week, day_name;
