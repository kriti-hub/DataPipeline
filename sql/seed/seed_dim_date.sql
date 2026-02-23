-- ============================================================================
-- File:        seed_dim_date.sql
-- Description: Populates the dim_date dimension table with two years of
--              pre-computed date records from 2025-01-01 to 2026-12-31.
--              Uses BigQuery's GENERATE_DATE_ARRAY to produce all dates
--              and computes calendar attributes for each.
-- Table:       people_analytics.dim_date
-- ============================================================================

INSERT INTO people_analytics.dim_date (
  date_key,
  full_date,
  year,
  quarter,
  month,
  month_name,
  week_of_year,
  day_of_week,
  day_name,
  is_weekend,
  is_month_end,
  fiscal_year,
  fiscal_quarter
)
SELECT
  -- date_key: integer in YYYYMMDD format
  CAST(FORMAT_DATE('%Y%m%d', d) AS INT64) AS date_key,

  -- full_date: the DATE value
  d AS full_date,

  -- year
  EXTRACT(YEAR FROM d) AS year,

  -- quarter (1-4)
  EXTRACT(QUARTER FROM d) AS quarter,

  -- month (1-12)
  EXTRACT(MONTH FROM d) AS month,

  -- month_name (January, February, ...)
  FORMAT_DATE('%B', d) AS month_name,

  -- week_of_year (ISO week number, 1-53)
  EXTRACT(ISOWEEK FROM d) AS week_of_year,

  -- day_of_week: 1=Sunday, 2=Monday, ..., 7=Saturday
  EXTRACT(DAYOFWEEK FROM d) AS day_of_week,

  -- day_name (Sunday, Monday, ...)
  FORMAT_DATE('%A', d) AS day_name,

  -- is_weekend: TRUE if Saturday (7) or Sunday (1)
  EXTRACT(DAYOFWEEK FROM d) IN (1, 7) AS is_weekend,

  -- is_month_end: TRUE if this date is the last day of its month
  d = DATE_SUB(DATE_TRUNC(DATE_ADD(d, INTERVAL 1 MONTH), MONTH), INTERVAL 1 DAY) AS is_month_end,

  -- fiscal_year: assumes calendar year = fiscal year
  EXTRACT(YEAR FROM d) AS fiscal_year,

  -- fiscal_quarter: assumes calendar quarter = fiscal quarter
  EXTRACT(QUARTER FROM d) AS fiscal_quarter

FROM
  UNNEST(GENERATE_DATE_ARRAY(DATE '2025-01-01', DATE '2026-12-31', INTERVAL 1 DAY)) AS d
ORDER BY
  d;
