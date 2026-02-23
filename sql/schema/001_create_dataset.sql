-- ============================================================================
-- File:        001_create_dataset.sql
-- Description: Creates the people_analytics dataset in BigQuery.
--              This is the top-level container for all dimension, fact,
--              and utility tables in the WellNow Staffing Analytics warehouse.
-- Dataset:     people_analytics
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS people_analytics
OPTIONS (
  description = 'WellNow Urgent Care People Analytics data warehouse. Contains dimension tables (employee, location, job, date), fact tables (daily staffing, shift gaps), and utility tables (pipeline runs, data quality log, quarantine) for multi-location workforce staffing and coverage optimization.',
  location = 'US'
);
