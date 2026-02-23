-- ============================================================================
-- File:        002_create_dim_employee.sql
-- Description: Creates the dim_employee dimension table (SCD Type 2).
--              Stores employee/clinician records with historical tracking
--              of job title, location, and status changes over time.
-- Table:       people_analytics.dim_employee
-- ============================================================================

CREATE TABLE IF NOT EXISTS people_analytics.dim_employee (
  employee_key        INT64 NOT NULL,       -- Surrogate key
  employee_id         STRING NOT NULL,       -- Natural key (EMP-XXXXX)
  first_name          STRING,
  last_name           STRING,
  full_name           STRING,                -- Derived: first_name || ' ' || last_name
  email               STRING,
  hire_date           DATE NOT NULL,
  termination_date    DATE,
  status              STRING NOT NULL,       -- Active, Terminated, Leave
  role_type           STRING NOT NULL,       -- Provider, RN, MA, RadTech, OfficeMgr, FrontDesk
  job_title           STRING,
  job_level           STRING,
  is_provider         BOOL,                  -- Derived: role_type IN ('Provider')
  is_people_manager   BOOL,
  schedule_type       STRING,                -- Full-time, Part-time, PRN/Float
  location_key        INT64,
  manager_employee_id STRING,
  tenure_years        FLOAT64,
  tenure_band         STRING,                -- Derived: 0-1yr, 1-3yr, 3-5yr, 5-10yr, 10+yr
  is_new_hire         BOOL,                  -- Derived: hire_date within last 90 days
  -- SCD Type 2 fields
  effective_start     DATE NOT NULL,
  effective_end       DATE,
  is_current          BOOL NOT NULL,
  -- Metadata
  _loaded_at          TIMESTAMP NOT NULL,
  _source_system      STRING DEFAULT 'hris_api',
  _batch_id           STRING
)
CLUSTER BY location_key, role_type, status;
