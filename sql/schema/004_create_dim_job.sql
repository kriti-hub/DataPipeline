-- ============================================================================
-- File:        004_create_dim_job.sql
-- Description: Creates the dim_job dimension table.
--              Stores job title reference data with role classification
--              flags for clinical and provider designations.
-- Table:       people_analytics.dim_job
-- ============================================================================

CREATE TABLE IF NOT EXISTS people_analytics.dim_job (
  job_key         INT64 NOT NULL,
  job_title       STRING NOT NULL,
  role_type       STRING NOT NULL,     -- Provider, RN, MA, RadTech, OfficeMgr, FrontDesk
  job_level       STRING,
  is_clinical     BOOL,                -- TRUE for Provider, RN, MA, RadTech
  is_provider     BOOL,                -- TRUE for MD/DO/PA/NP only
  _loaded_at      TIMESTAMP NOT NULL
);
