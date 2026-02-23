# Data Dictionary -- WellNow Staffing Analytics

**Dataset:** `people_analytics` (Google BigQuery)
**Last Updated:** 2026-02-22
**Owner:** Data Engineering / People Analytics Team

---

## Table of Contents

1. [Dimension Tables](#dimension-tables)
   - [dim_employee](#dim_employee)
   - [dim_location](#dim_location)
   - [dim_job](#dim_job)
   - [dim_date](#dim_date)
2. [Fact Tables](#fact-tables)
   - [fact_daily_staffing](#fact_daily_staffing)
   - [fact_shift_gap](#fact_shift_gap)
3. [Pipeline Metadata Tables](#pipeline-metadata-tables)
   - [_pipeline_runs](#_pipeline_runs)
   - [_data_quality_log](#_data_quality_log)
   - [_quarantine](#_quarantine)
4. [Source System Reference](#source-system-reference)
5. [Enumeration Values Reference](#enumeration-values-reference)
6. [Conventions](#conventions)

---

## Conventions

- **Surrogate keys** use the suffix `_key` and are auto-generated INT64 values with no business meaning.
- **Natural keys** use the suffix `_id` and originate from the source system.
- **Foreign keys** reference surrogate keys in dimension tables unless otherwise noted.
- **SCD Type 2** columns (`effective_start`, `effective_end`, `is_current`) track historical changes. Only the row where `is_current = TRUE` reflects the present state.
- **ETL metadata** columns prefixed with `_` (`_loaded_at`, `_source_system`, `_batch_id`) are populated by the pipeline and are not business-facing.
- **DERIVED** fields are computed during the ETL transform stage; they do not exist in the raw source data.
- All timestamps are in **UTC**.
- All monetary values are in **USD**.

---

## Dimension Tables

### dim_employee

Slowly Changing Dimension (Type 2) tracking every employee who has worked at a WellNow Urgent Care location. Each row represents a version of the employee record valid between `effective_start` and `effective_end`. The current version is identified by `is_current = TRUE`.

**Source:** Simulated HRIS API -- `/workers` and `/terminations` endpoints.

| Field | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `employee_key` | INT64 | NOT NULL | Surrogate key. Auto-generated identifier unique to each SCD2 row version. | `1001` |
| `employee_id` | STRING | NOT NULL | Natural key from the HRIS. Format: `EMP-XXXXX`. Stable across SCD2 row versions. | `"EMP-00142"` |
| `first_name` | STRING | Nullable | Employee first name. | `"Sarah"` |
| `last_name` | STRING | Nullable | Employee last name. | `"Johnson"` |
| `full_name` | STRING | Nullable | **DERIVED.** Concatenation of first and last name. **Formula:** `first_name \|\| ' ' \|\| last_name` | `"Sarah Johnson"` |
| `email` | STRING | Nullable | Corporate email address. | `"sarah.johnson@wellnow.com"` |
| `hire_date` | DATE | NOT NULL | Date the employee was hired. Used as the baseline for tenure calculations. | `2024-03-15` |
| `termination_date` | DATE | Nullable | Date employment ended. `NULL` if the employee is currently active. | `2025-11-30` or `NULL` |
| `status` | STRING | NOT NULL | Current employment status. Enumeration: `Active`, `Terminated`, `Leave`. | `"Active"` |
| `role_type` | STRING | NOT NULL | Standardized role classification. Enumeration: `Provider`, `RN`, `MA`, `RadTech`, `OfficeMgr`, `FrontDesk`. | `"Provider"` |
| `job_title` | STRING | Nullable | Full job title as recorded in the HRIS. | `"Nurse Practitioner"` |
| `job_level` | STRING | Nullable | Job level or grade (e.g., senior, lead) if applicable. | `"Senior"` |
| `is_provider` | BOOL | Nullable | **DERIVED.** Indicates whether the employee is a licensed provider (MD, DO, PA, NP). **Formula:** `TRUE` when `role_type = 'Provider'`. | `TRUE` |
| `is_people_manager` | BOOL | Nullable | Indicates whether the employee manages other employees. | `FALSE` |
| `schedule_type` | STRING | Nullable | Work schedule classification. Enumeration: `Full-time`, `Part-time`, `PRN`, `Float`. | `"Full-time"` |
| `location_key` | INT64 | Nullable | Foreign key to `dim_location`. The employee's primary assigned clinic. | `501` |
| `manager_employee_id` | STRING | Nullable | Self-referencing foreign key to `employee_id` of the employee's direct manager. | `"EMP-00023"` |
| `tenure_years` | FLOAT64 | Nullable | Number of years since `hire_date`, updated each pipeline run. | `1.85` |
| `tenure_band` | STRING | Nullable | **DERIVED.** Bucketed tenure for reporting. **Formula:** Based on `tenure_years`: `0-1yr` (< 1), `1-3yr` (>= 1 and < 3), `3-5yr` (>= 3 and < 5), `5-10yr` (>= 5 and < 10), `10+yr` (>= 10). | `"1-3yr"` |
| `is_new_hire` | BOOL | Nullable | **DERIVED.** Flags employees hired within the last 90 calendar days. **Formula:** `TRUE` if `hire_date >= CURRENT_DATE() - 90`. | `TRUE` |
| `effective_start` | DATE | NOT NULL | SCD2 metadata. The date this row version became valid. | `2025-06-01` |
| `effective_end` | DATE | Nullable | SCD2 metadata. The date this row version was superseded. `NULL` if this is the current version. | `2025-12-31` or `NULL` |
| `is_current` | BOOL | NOT NULL | SCD2 metadata. `TRUE` for the currently active row version; `FALSE` for historical versions. | `TRUE` |
| `_loaded_at` | TIMESTAMP | NOT NULL | ETL metadata. UTC timestamp when the row was written to BigQuery. | `2026-01-15 03:22:10 UTC` |
| `_source_system` | STRING | NOT NULL | ETL metadata. Identifier of the originating system. Default: `'hris_api'`. | `"hris_api"` |
| `_batch_id` | STRING | Nullable | ETL metadata. Unique identifier for the pipeline run that produced this row. | `"run-2026-01-15-0322"` |

**Key relationships:**
- `location_key` references `dim_location.location_key`.
- `manager_employee_id` self-references `dim_employee.employee_id`.
- Referenced by `fact_daily_staffing` and `fact_shift_gap` through `location_key`.

---

### dim_location

Reference dimension for all WellNow Urgent Care clinic locations. Each row represents one physical clinic. This is not an SCD table; updates overwrite in place.

**Source:** Simulated HRIS API -- `/locations` endpoint.

| Field | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `location_key` | INT64 | NOT NULL | Surrogate key. Auto-generated unique identifier. | `501` |
| `location_id` | STRING | NOT NULL | Natural key from the source system. Format: `LOC-XXX`. | `"LOC-042"` |
| `location_name` | STRING | NOT NULL | Human-readable clinic name. | `"WellNow Syracuse East"` |
| `region` | STRING | NOT NULL | Geographic region the clinic belongs to. | `"Northeast"` |
| `state` | STRING | NOT NULL | US state abbreviation (two-letter code). | `"NY"` |
| `metro_area` | STRING | Nullable | Metropolitan statistical area. May be `NULL` for rural locations. | `"Syracuse"` |
| `location_type` | STRING | NOT NULL | Classification of the location's setting. Enumeration: `Urban`, `Suburban`, `Rural`. | `"Suburban"` |
| `operating_hours_start` | STRING | Nullable | Clinic opening time in 24-hour `HH:MM` format. | `"08:00"` |
| `operating_hours_end` | STRING | Nullable | Clinic closing time in 24-hour `HH:MM` format. | `"20:00"` |
| `days_open_per_week` | INT64 | Nullable | Number of days the clinic is open each week. Range: 1--7. | `7` |
| `budgeted_provider_fte` | FLOAT64 | Nullable | Target full-time equivalent headcount for providers at this location. Used in gap analysis. | `4.5` |
| `budgeted_support_fte` | FLOAT64 | Nullable | Target full-time equivalent headcount for non-provider clinical and administrative staff. | `8.0` |
| `opened_date` | DATE | Nullable | Date the clinic first opened for patient visits. | `2019-06-15` |
| `is_active` | BOOL | NOT NULL | Whether the location is currently operational. Default: `TRUE`. | `TRUE` |
| `_loaded_at` | TIMESTAMP | NOT NULL | ETL metadata. UTC timestamp when the row was written to BigQuery. | `2026-01-15 03:22:10 UTC` |

**Key relationships:**
- Referenced by `dim_employee.location_key`.
- Referenced by `fact_daily_staffing.location_key`.
- Referenced by `fact_shift_gap.location_key`.

---

### dim_job

Conformed dimension for job titles and role classifications. Provides a standardized mapping between job titles and the role taxonomy used across the analytics dataset.

**Source:** Simulated HRIS API -- `/workers` endpoint (distinct job records).

| Field | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `job_key` | INT64 | NOT NULL | Surrogate key. Auto-generated unique identifier. | `201` |
| `job_title` | STRING | NOT NULL | Standard job title. | `"Physician Assistant"` |
| `role_type` | STRING | NOT NULL | Standardized role classification. Enumeration: `Provider`, `RN`, `MA`, `RadTech`, `OfficeMgr`, `FrontDesk`. | `"Provider"` |
| `job_level` | STRING | Nullable | Job level or grade if applicable. | `"Senior"` |
| `is_clinical` | BOOL | Nullable | Indicates whether the role involves direct clinical care. `TRUE` for `Provider`, `RN`, `MA`, `RadTech`. | `TRUE` |
| `is_provider` | BOOL | Nullable | Indicates whether the role is a licensed provider (MD, DO, PA, NP). `TRUE` only for `role_type = 'Provider'`. | `TRUE` |
| `_loaded_at` | TIMESTAMP | NOT NULL | ETL metadata. UTC timestamp when the row was written to BigQuery. | `2026-01-15 03:22:10 UTC` |

**Key relationships:**
- Can be joined to `dim_employee` on `job_title` and/or `role_type` for role-based analysis.

---

### dim_date

Standard calendar dimension pre-populated with one row per calendar date. Used as the time spine for all fact tables. Includes both calendar and fiscal year attributes.

**Source:** Generated during initial dataset setup; not sourced from the HRIS API.

| Field | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `date_key` | INT64 | NOT NULL | Surrogate key in `YYYYMMDD` integer format. | `20260115` |
| `full_date` | DATE | NOT NULL | The calendar date. | `2026-01-15` |
| `year` | INT64 | NOT NULL | Four-digit calendar year. | `2026` |
| `quarter` | INT64 | NOT NULL | Calendar quarter (1--4). | `1` |
| `month` | INT64 | NOT NULL | Calendar month (1--12). | `1` |
| `month_name` | STRING | NOT NULL | Full name of the calendar month. | `"January"` |
| `week_of_year` | INT64 | NOT NULL | ISO week number (1--53). | `3` |
| `day_of_week` | INT64 | NOT NULL | Day of week as an integer. 1 = Sunday, 2 = Monday, ..., 7 = Saturday. | `4` |
| `day_name` | STRING | NOT NULL | Full name of the day of the week. | `"Wednesday"` |
| `is_weekend` | BOOL | NOT NULL | `TRUE` if the date falls on Saturday or Sunday. | `FALSE` |
| `is_month_end` | BOOL | NOT NULL | `TRUE` if the date is the last day of the calendar month. | `FALSE` |
| `fiscal_year` | INT64 | NOT NULL | TAG (The Aspen Group) fiscal year. May differ from calendar year depending on fiscal calendar definition. | `2026` |
| `fiscal_quarter` | INT64 | NOT NULL | TAG fiscal quarter (1--4). | `1` |

**Key relationships:**
- Referenced by `fact_daily_staffing.date_key`.
- Referenced by `fact_shift_gap.date_key`.

---

## Fact Tables

### fact_daily_staffing

Grain: one row per **location per day**. Captures daily staffing levels, patient volume, cost, and efficiency metrics for each WellNow clinic. This is the primary fact table for operational dashboards.

**Partitioning:** Partitioned by `snapshot_date`.
**Clustering:** Clustered by `location_key`.

**Source:** Simulated HRIS API -- `/schedules` and `/patient-volume` endpoints, combined and aggregated during the ETL transform stage.

| Field | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `date_key` | INT64 | NOT NULL | Foreign key to `dim_date`. Encoded as `YYYYMMDD`. | `20260115` |
| `snapshot_date` | DATE | NOT NULL | The calendar date this row describes. Also serves as the BigQuery partition key. | `2026-01-15` |
| `location_key` | INT64 | NOT NULL | Foreign key to `dim_location`. The clinic this row describes. | `501` |
| `scheduled_provider_hours` | FLOAT64 | Nullable | Total provider hours that were scheduled for the day. | `32.0` |
| `actual_provider_hours` | FLOAT64 | Nullable | Total provider hours actually worked, accounting for callouts, late arrivals, and early departures. | `28.5` |
| `required_provider_hours` | FLOAT64 | Nullable | Demand-based required provider hours derived from patient volume forecasts and staffing models. | `30.0` |
| `scheduled_support_hours` | FLOAT64 | Nullable | Total non-provider staff hours scheduled (RN, MA, RadTech, front desk, office manager). | `64.0` |
| `actual_support_hours` | FLOAT64 | Nullable | Total non-provider staff hours actually worked. | `60.0` |
| `overtime_hours` | FLOAT64 | Nullable | Total hours worked beyond standard shift thresholds, across all staff at the location. | `4.5` |
| `callout_count` | INT64 | Nullable | Number of shift callouts (unplanned absences) for the day at this location. | `2` |
| `patient_visits` | INT64 | Nullable | Total patient visits (encounters) for the day. | `85` |
| `patients_per_provider_hour` | FLOAT64 | Nullable | **DERIVED.** Productivity metric: average patients seen per provider hour worked. **Formula:** `patient_visits / actual_provider_hours`. Returns `NULL` if `actual_provider_hours` is `NULL` or zero. | `2.98` |
| `avg_wait_time_minutes` | FLOAT64 | Nullable | Average patient wait time in minutes from check-in to provider encounter. | `18.5` |
| `coverage_score` | FLOAT64 | Nullable | **DERIVED.** Ratio of actual staffing to demand-based requirement. A score of 1.0 means exact coverage. **Formula:** `actual_provider_hours / required_provider_hours`. Returns `NULL` if `required_provider_hours` is `NULL` or zero. **Business definition:** Values below 1.0 indicate understaffing; values above 1.0 indicate overstaffing relative to demand. | `0.95` |
| `labor_cost_total` | FLOAT64 | Nullable | Total labor cost (USD) for all staff at the location on this day, inclusive of overtime premiums. | `8540.00` |
| `labor_cost_per_visit` | FLOAT64 | Nullable | **DERIVED.** Unit economics metric: labor cost per patient encounter. **Formula:** `labor_cost_total / patient_visits`. Returns `NULL` if `patient_visits` is `NULL` or zero. | `100.47` |
| `_loaded_at` | TIMESTAMP | NOT NULL | ETL metadata. UTC timestamp when the row was written to BigQuery. | `2026-01-15 03:22:10 UTC` |
| `_batch_id` | STRING | Nullable | ETL metadata. Unique identifier for the pipeline run that produced this row. | `"run-2026-01-15-0322"` |

**Key relationships:**
- `date_key` references `dim_date.date_key`.
- `location_key` references `dim_location.location_key`.
- Can be joined to `dim_employee` via `location_key` for employee-level attribution.

---

### fact_shift_gap

Grain: one row per **location per day per shift window**. Provides sub-daily granularity for identifying staffing gaps and excess coverage within specific time blocks. This table drives the shift gap alert system.

**Partitioning:** Partitioned by `snapshot_date`.
**Clustering:** Clustered by `location_key`, `shift_window`.

**Source:** Simulated HRIS API -- `/schedules` endpoint, disaggregated by shift window during ETL.

| Field | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `date_key` | INT64 | NOT NULL | Foreign key to `dim_date`. Encoded as `YYYYMMDD`. | `20260115` |
| `snapshot_date` | DATE | NOT NULL | The calendar date this row describes. Also serves as the BigQuery partition key. | `2026-01-15` |
| `location_key` | INT64 | NOT NULL | Foreign key to `dim_location`. The clinic this row describes. | `501` |
| `shift_window` | STRING | NOT NULL | Time block within the day. Enumeration: `AM` (08:00--12:00), `PM` (12:00--16:00), `Evening` (16:00--20:00). | `"AM"` |
| `required_providers` | INT64 | Nullable | Number of providers required for this shift window based on demand models. | `3` |
| `scheduled_providers` | INT64 | Nullable | Number of providers originally scheduled for this shift window. | `3` |
| `actual_providers` | INT64 | Nullable | Number of providers who actually worked this shift window, net of callouts and replacements. | `2` |
| `gap_flag` | BOOL | Nullable | **DERIVED.** Indicates the shift window was understaffed relative to requirements. **Formula:** `TRUE` when `actual_providers < required_providers`. **Business definition:** A gap means patients may experience longer wait times or be redirected to another location. | `TRUE` |
| `excess_flag` | BOOL | Nullable | **DERIVED.** Indicates the shift window was overstaffed beyond a 15% buffer. **Formula:** `TRUE` when `actual_providers > required_providers * 1.15`. **Business definition:** Excess staffing represents an opportunity to redeploy providers to gap locations or reduce labor cost. | `FALSE` |
| `gap_hours` | FLOAT64 | Nullable | Total hours of unfilled provider time within the shift window. Calculated as the difference between required and actual provider hours when a gap exists. | `4.0` |
| `excess_hours` | FLOAT64 | Nullable | Total hours of excess provider time within the shift window beyond the 15% buffer. | `0.0` |
| `_loaded_at` | TIMESTAMP | NOT NULL | ETL metadata. UTC timestamp when the row was written to BigQuery. | `2026-01-15 03:22:10 UTC` |
| `_batch_id` | STRING | Nullable | ETL metadata. Unique identifier for the pipeline run that produced this row. | `"run-2026-01-15-0322"` |

**Key relationships:**
- `date_key` references `dim_date.date_key`.
- `location_key` references `dim_location.location_key`.
- Can be aggregated up to daily grain to reconcile with `fact_daily_staffing`.

---

## Pipeline Metadata Tables

These tables are internal to the data pipeline. They are prefixed with `_` to indicate they are not business-facing and should not appear in end-user dashboards. They support pipeline observability, data quality monitoring, and incident response.

### _pipeline_runs

Grain: one row per **pipeline execution**. Provides an audit trail of every ETL run, including record counts and error details.

**Source:** Populated by the orchestration layer at the start and end of each pipeline run.

| Field | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `run_id` | STRING | NOT NULL | Primary key. UUID uniquely identifying this pipeline execution. | `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"` |
| `pipeline_name` | STRING | NOT NULL | Name of the pipeline or DAG that was executed. | `"daily_staffing_etl"` |
| `started_at` | TIMESTAMP | NOT NULL | UTC timestamp when the pipeline run began. | `2026-01-15 03:00:00 UTC` |
| `completed_at` | TIMESTAMP | Nullable | UTC timestamp when the pipeline run finished. `NULL` if still in progress or crashed without completing. | `2026-01-15 03:22:10 UTC` |
| `status` | STRING | NOT NULL | Outcome of the pipeline run. Enumeration: `Success` (all stages completed), `Failed` (pipeline halted on error), `Partial` (some stages succeeded, others failed). | `"Success"` |
| `records_extracted` | INT64 | Nullable | Count of records pulled from the source system. | `1250` |
| `records_validated` | INT64 | Nullable | Count of records that passed all data quality checks. | `1238` |
| `records_quarantined` | INT64 | Nullable | Count of records that failed data quality checks and were routed to the `_quarantine` table. | `12` |
| `records_loaded` | INT64 | Nullable | Count of records successfully written to destination tables. | `1238` |
| `error_message` | STRING | Nullable | Error details if the pipeline failed or partially failed. `NULL` on success. | `"Timeout connecting to HRIS API"` |
| `run_duration_seconds` | FLOAT64 | Nullable | Wall-clock duration of the pipeline run in seconds. | `1330.5` |
| `_batch_id` | STRING | Nullable | Batch identifier, typically equal to `run_id` for traceability. | `"run-2026-01-15-0322"` |

---

### _data_quality_log

Grain: one row per **data quality check per day**. Records the results of automated data quality checks run during each pipeline execution.

**Source:** Populated by the data quality framework during the ETL validation stage.

| Field | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `check_date` | DATE | NOT NULL | The date the data quality check was executed. | `2026-01-15` |
| `check_name` | STRING | NOT NULL | Unique identifier for the data quality rule. Format: `DQ-XXX`. | `"DQ-001"` |
| `table_name` | STRING | NOT NULL | The target table being validated. | `"fact_daily_staffing"` |
| `check_type` | STRING | NOT NULL | Category of the data quality check. Examples: `null_check`, `range_check`, `uniqueness_check`, `referential_integrity`, `freshness_check`. | `"null_check"` |
| `records_checked` | INT64 | Nullable | Total number of records evaluated by the check. | `1250` |
| `records_passed` | INT64 | Nullable | Number of records that met the quality criteria. | `1238` |
| `records_failed` | INT64 | Nullable | Number of records that violated the quality criteria. | `12` |
| `pass_rate` | FLOAT64 | Nullable | Fraction of records that passed. Range: `0.0` to `1.0`. Calculated as `records_passed / records_checked`. | `0.9904` |
| `severity` | STRING | NOT NULL | Impact level if the check fails. Enumeration: `Critical` (pipeline halts), `High` (alert + investigation required), `Medium` (warning logged), `Low` (informational). | `"High"` |
| `status` | STRING | NOT NULL | Outcome of the check. Enumeration: `Pass` (within acceptable thresholds), `Warn` (degraded but within tolerance), `Fail` (threshold breached). | `"Pass"` |
| `details` | STRING | Nullable | Free-text description of the check result, including specifics of any failures. | `"12 records missing location_key"` |
| `_batch_id` | STRING | Nullable | ETL metadata. Pipeline run identifier for traceability. | `"run-2026-01-15-0322"` |

---

### _quarantine

Grain: one row per **quarantined record**. Stores records that failed data quality checks during the ETL validation stage. These records are excluded from the destination tables and held here for investigation and potential reprocessing.

**Source:** Populated by the data quality framework when a record fails a validation rule.

| Field | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `quarantine_date` | TIMESTAMP | NOT NULL | UTC timestamp when the record was quarantined. | `2026-01-15 03:15:42 UTC` |
| `source_table` | STRING | NOT NULL | The destination table the record was intended for before it failed validation. | `"fact_daily_staffing"` |
| `record_json` | STRING | Nullable | The full original record serialized as a JSON string for inspection and reprocessing. | `"{\"location_id\": \"LOC-042\", ...}"` |
| `failure_rule_id` | STRING | Nullable | The `check_name` from `_data_quality_log` that triggered quarantine. | `"DQ-001"` |
| `failure_reason` | STRING | Nullable | Human-readable explanation of why the record was quarantined. | `"location_key is NULL"` |
| `_batch_id` | STRING | Nullable | ETL metadata. Pipeline run identifier for traceability. | `"run-2026-01-15-0322"` |

---

## Source System Reference

All raw data originates from the **Simulated HRIS API**. The table below maps each API endpoint to the tables it feeds.

| API Endpoint | Description | Destination Tables |
|---|---|---|
| `/workers` | Employee demographic and role data | `dim_employee`, `dim_job` |
| `/terminations` | Termination records with dates and reasons | `dim_employee` (termination_date, status) |
| `/locations` | Clinic locations, operating hours, and FTE budgets | `dim_location` |
| `/schedules` | Shift schedules and actual hours worked | `fact_daily_staffing`, `fact_shift_gap` |
| `/patient-volume` | Daily patient visit counts and wait times | `fact_daily_staffing` |

All derived fields (marked **DERIVED** in the tables above) are computed in the **ETL transform stage** and do not exist in the raw API responses.

---

## Enumeration Values Reference

Quick reference for all enumerated string fields across the dataset.

| Table | Field | Valid Values |
|---|---|---|
| `dim_employee` | `status` | `Active`, `Terminated`, `Leave` |
| `dim_employee` | `role_type` | `Provider`, `RN`, `MA`, `RadTech`, `OfficeMgr`, `FrontDesk` |
| `dim_employee` | `schedule_type` | `Full-time`, `Part-time`, `PRN`, `Float` |
| `dim_employee` | `tenure_band` | `0-1yr`, `1-3yr`, `3-5yr`, `5-10yr`, `10+yr` |
| `dim_location` | `location_type` | `Urban`, `Suburban`, `Rural` |
| `dim_job` | `role_type` | `Provider`, `RN`, `MA`, `RadTech`, `OfficeMgr`, `FrontDesk` |
| `fact_shift_gap` | `shift_window` | `AM` (08:00--12:00), `PM` (12:00--16:00), `Evening` (16:00--20:00) |
| `_pipeline_runs` | `status` | `Success`, `Failed`, `Partial` |
| `_data_quality_log` | `severity` | `Critical`, `High`, `Medium`, `Low` |
| `_data_quality_log` | `status` | `Pass`, `Warn`, `Fail` |
