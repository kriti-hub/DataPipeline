-- ============================================================================
-- File:        005_create_dim_date.sql
-- Description: Creates the dim_date dimension table.
--              Stores pre-computed date attributes for efficient date-based
--              joins and filtering in analytics queries.
-- Table:       people_analytics.dim_date
-- ============================================================================

CREATE TABLE IF NOT EXISTS people_analytics.dim_date (
  date_key        INT64 NOT NULL,       -- YYYYMMDD format
  full_date       DATE NOT NULL,
  year            INT64,
  quarter         INT64,
  month           INT64,
  month_name      STRING,
  week_of_year    INT64,
  day_of_week     INT64,               -- 1=Sunday ... 7=Saturday
  day_name        STRING,
  is_weekend      BOOL,
  is_month_end    BOOL,
  fiscal_year     INT64,
  fiscal_quarter  INT64
);
