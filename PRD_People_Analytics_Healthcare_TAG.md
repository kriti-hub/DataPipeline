# Product Requirements Document (PRD)
# People Analytics Data Pipeline — Healthcare Workforce Optimization POC
### Multi-Location Staffing & Coverage Intelligence for WellNow Urgent Care

**Version:** 3.0
**Date:** February 22, 2026
**Candidate:** Kriti Srivastava
**Target Role:** Senior Analyst, Data & Insights — WellNow Urgent Care (TAG)
**Status:** Final — Ready for Architecture Design & Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Use Case Prioritization Framework](#2-use-case-prioritization-framework)
3. [Use Case: Multi-Location Workforce Staffing & Coverage Optimization](#3-use-case-multi-location-workforce-staffing--coverage-optimization)
4. [Architecture Overview](#4-architecture-overview)
5. [Simulated HRIS API Specification](#5-simulated-hris-api-specification)
6. [ETL Pipeline Specification](#6-etl-pipeline-specification)
7. [BigQuery Data Warehouse Schema](#7-bigquery-data-warehouse-schema)
8. [Data Quality Framework](#8-data-quality-framework)
9. [Dashboard Specification](#9-dashboard-specification)
10. [Enterprise File Structure & Repository Layout](#10-enterprise-file-structure--repository-layout)
11. [Security, Privacy & Compliance](#11-security-privacy--compliance)
12. [Development Phases](#12-development-phases)
13. [Cost Budget](#13-cost-budget)
14. [Skills Demonstrated → Job Requirements Mapping](#14-skills-demonstrated--job-requirements-mapping)
15. [Out of Scope (v1)](#15-out-of-scope-v1)
16. [Claude Code Implementation Instructions](#16-claude-code-implementation-instructions)

---

## 1. Executive Summary

This PRD defines a **single, deeply-scoped** proof-of-concept: a live, end-to-end People Analytics data pipeline and interactive dashboard focused on **Multi-Location Workforce Staffing & Coverage Optimization** for urgent care operations.

The POC is purpose-built to demonstrate production-grade data engineering skills directly aligned with the **Senior Analyst, Data & Insights** role supporting **WellNow Urgent Care** at **TAG — The Aspen Group**.

### About TAG — The Aspen Group

TAG is one of the largest retail healthcare support organizations in the U.S.:

- **15,000+** healthcare professionals and team members
- **1,400+** locations across **48 states**
- **5 brands:** Aspen Dental, ClearChoice Dental Implant Centers, WellNow Urgent Care, Chapter Aesthetic Studio, Lovet Pet Health Care
- **$4.2B** annualized net revenue (H1 2025, +8% YoY)
- **35,000+** patients served daily; **9M+** annually
- Named to Built In's **2026 Best Large Places to Work**

### What This POC Delivers

A simulated multi-location urgent care staffing environment that models realistic workforce data, runs real Python ETL into BigQuery on GCP, and serves live operational analytics through an interactive React dashboard — all within GCP's free tier ($0/month).

**Core Message:** *"I built the exact data infrastructure this role requires — a working pipeline from HRIS to BigQuery with multi-location staffing intelligence, coverage gap analysis, and labor cost optimization — as a solo project, using the tools TAG uses (BigQuery, SQL, data visualization)."*

---

## 2. Use Case Prioritization Framework

Three candidate use cases were evaluated for this POC. A weighted scoring model was used to select the single highest-impact use case that demonstrates the most relevant skills for the WellNow Senior Analyst role while addressing TAG's most pressing business needs.

### Candidate Use Cases

| # | Use Case | Description |
|---|---|---|
| UC-1 | Multi-Brand Clinician Retention & Attrition Intelligence | Cross-brand view of where TAG is losing talent, why, and whether TAG University programs are driving retention |
| UC-2 | Multi-Location Workforce Staffing & Coverage Optimization | Location-level staffing efficiency, coverage gaps, overtime hotspots, and float clinician deployment for WellNow |
| UC-3 | Compensation Competitiveness & Pay Equity Analytics | Enterprise-wide compa-ratio analysis across 5 brands and 48 states, gender pay equity, cost-to-market modeling |

### Scoring Criteria

Two primary factors were evaluated, each with sub-dimensions weighted by relevance to the WellNow Senior Analyst role and TAG's stated strategic priorities.

---

### Factor 1: Importance to Customer (Patient) Needs

The healthcare business exists to serve patients. The use case that most directly connects workforce data to patient experience outcomes earns the highest score.

| Sub-Dimension | Weight | UC-1 (Retention) | UC-2 (Staffing) | UC-3 (Comp) |
|---|---|---|---|---|
| **Patient wait times** — Does the analysis directly reduce patient wait times? | 25% | Indirect. Lower turnover means more experienced staff, but the linkage to wait times is second-order. | **Direct.** Coverage gap analysis identifies understaffed shifts that cause long wait times. Float deployment recommendations reduce gaps in real-time. | None. Compensation analysis does not affect day-to-day patient wait times. |
| **Chair/room utilization** — Does the analysis improve how efficiently clinical capacity is used? | 25% | Indirect. Retention keeps chairs filled longer-term, but doesn't optimize daily utilization. | **Direct.** Staff-to-patient ratio analysis and shift-level coverage scoring measure exactly whether clinical capacity is being utilized or wasted. | None. |
| **Profitability per location** — Does the analysis help leadership understand and improve per-location economics? | 25% | Indirect. Retention reduces replacement costs (~213% of salary per exit), but the per-location P&L linkage is diffuse. | **Direct.** Labor cost per patient visit, overtime spend, and coverage efficiency are the primary levers of per-location profitability. Labor is the single largest variable expense for healthcare organizations. | Moderate. Compensation optimization affects cost structure, but at an enterprise level rather than per-location. |
| **Service continuity** — Does the analysis prevent disruptions to patient care delivery? | 25% | Moderate. Reducing attrition prevents long-term staffing holes, but doesn't address day-to-day coverage. | **Direct.** Shift gap detection and callout tracking directly prevent same-day and same-week care delivery disruptions. | None. |

**Factor 1 Scores:**

| Use Case | Score (0–5) | Rationale |
|---|---|---|
| UC-1 (Retention) | 2.5 | Important but indirect — affects patient experience through second-order workforce stability effects |
| **UC-2 (Staffing)** | **4.8** | **Directly connects workforce data to the patient-facing metrics that matter most: wait times, utilization, cost, and continuity** |
| UC-3 (Comp) | 1.5 | Primarily an internal HR/Finance concern — minimal direct patient impact |

---

### Factor 2: Alignment with Business Growth (ROI)

TAG grew revenue 8% YoY in H1 2025 while expanding to 1,429 locations. Growth at this scale requires operational efficiency — not just adding locations, but making each location perform better with existing resources.

#### Sub-Dimension 2A: Improving Employee Utilization — Reducing Overwork & Promoting Work-Life Balance

| Use Case | Impact | Detail |
|---|---|---|
| UC-1 (Retention) | Moderate | Identifies that burnout-driven attrition is happening, but doesn't show *where* overwork is occurring at a shift or location level. |
| **UC-2 (Staffing)** | **High** | Overtime tracking, callout pattern analysis, and coverage scoring directly identify which locations and shifts are overworking staff. Data-driven float deployment redistributes workload, reducing burnout at the source. When a clinic is chronically understaffed, it's not just a cost problem — it's the #1 driver of clinician burnout, which the AHA calls healthcare's top workforce challenge. This analysis gives operations the data to fix it. |
| UC-3 (Comp) | Low | Compensation adjustments don't address workload distribution. A well-paid clinician working 60-hour weeks due to understaffing still burns out. |

#### Sub-Dimension 2B: Improving Revenue per Clinician and Staff Member

| Use Case | Impact | Detail |
|---|---|---|
| UC-1 (Retention) | Moderate | Retaining experienced clinicians is important (they see more patients per hour), but this is a long-cycle metric. |
| **UC-2 (Staffing)** | **High** | Patients-per-provider-hour is a direct measure of revenue productivity. Coverage optimization ensures clinicians are deployed where patient demand exists — not sitting idle at overstaffed locations while another clinic turns patients away. Every unfilled shift gap at a WellNow clinic represents lost walk-in revenue that can *never* be recaptured (unlike dental, where appointments can be rescheduled). The analysis also identifies whether support staff ratios are enabling or constraining clinician productivity. |
| UC-3 (Comp) | Low-Moderate | Market-competitive compensation can reduce recruiting cycle times, getting clinicians into productive roles faster, but doesn't directly improve per-clinician revenue. |

**Factor 2 Scores:**

| Use Case | Score (0–5) | Rationale |
|---|---|---|
| UC-1 (Retention) | 3.0 | Valuable but addresses symptoms (attrition) more than root causes (workload imbalance) |
| **UC-2 (Staffing)** | **4.7** | **Directly improves both employee well-being (reducing overwork) and revenue generation (optimizing deployment). Addresses the root cause that drives both burnout and lost revenue.** |
| UC-3 (Comp) | 2.0 | Important for long-term talent strategy but limited short-term ROI on revenue or utilization |

---

### Final Prioritization Matrix

| Use Case | Factor 1: Customer Needs (50%) | Factor 2: Business Growth ROI (50%) | **Weighted Score** | **Rank** |
|---|---|---|---|---|
| UC-1: Clinician Retention | 2.5 | 3.0 | **2.75** | 2nd |
| **UC-2: Staffing Optimization** | **4.8** | **4.7** | **4.75** | **1st ✓** |
| UC-3: Compensation Analytics | 1.5 | 2.0 | **1.75** | 3rd |

### Decision

**Use Case 2 — Multi-Location Workforce Staffing & Coverage Optimization** is selected as the sole focus of this POC because:

1. **It directly impacts patient experience** — the metric TAG's business model depends on. Walk-in urgent care lives and dies on wait times and availability.
2. **It addresses both sides of the ROI equation** — reducing waste (overtime, overstaffing) while increasing revenue (filling coverage gaps where patient demand exists).
3. **It demonstrates the deepest range of analytical skills** — combining HRIS data, scheduling data, and patient volume data into operational intelligence.
4. **It is the most relevant to the WellNow Senior Analyst role** — the job description emphasizes working with WellNow field teams, understanding cross-departmental business impact, and building enterprise-wide reporting.
5. **It solves healthcare's #1 challenge** — workforce shortages and burnout — with data, not guesswork.

---

## 3. Use Case: Multi-Location Workforce Staffing & Coverage Optimization

### Business Problem

WellNow Urgent Care operates walk-in clinics across multiple states where **patient demand is variable and unpredictable** — driven by flu season, weather events, local outbreaks, and day-of-week patterns. Unlike scheduled dental appointments, urgent care requires real-time staffing adequacy. Every hour a clinic is understaffed means longer wait times, patient walkaways, and lost revenue. Every hour it's overstaffed means wasted labor dollars — the single largest variable expense for healthcare organizations.

TAG's field operations leaders need a data-driven view of **staffing efficiency across locations**: Which clinics are consistently understaffed? Which are overstaffed? Where are shift gaps creating coverage risks? How should float/PRN clinicians be deployed across a region?

This use case directly maps to the WellNow Senior Analyst role requirements:
- *"Working across departments to understand how their work impacts the performance of the business"*
- *"Combining multiple data sources; strong attention to detail and data integrity"*
- *"Synthesizing insights from various data sources and presenting data in an easy-to-read manner"*
- *"Utilizing data to uncover trends and insights, connecting changes in operational metrics to broader business performance"*

### Stakeholder Map

| Stakeholder | Seniority | What They Need | How They Use It |
|---|---|---|---|
| **WellNow Brand President** | Executive | Regional staffing efficiency scorecard | Weekly executive review — deciding where to invest in new hires vs. redistribute |
| **VP of Operations** | Senior Leadership | Location-level staff-to-patient ratio trends, coverage gap alerts | Operational reviews — holding regional directors accountable for staffing KPIs |
| **Regional Directors** | Mid-Management | Weekly staffing optimization recommendations | Tactical — deploying float clinicians, adjusting shift schedules |
| **Finance / FP&A** | Senior Leadership | Labor cost per patient visit by location, overtime trend analysis | Budget planning — forecasting labor spend, identifying cost reduction opportunities |
| **Recruiting / TA** | Mid-Management | Priority hiring locations based on chronic understaffing patterns | Hiring pipeline prioritization — where to focus sourcing efforts |
| **Clinic Office Managers** | Frontline | Their location's staffing scorecard vs. regional benchmarks | Self-service — understanding how their clinic performs relative to peers |

### Key Metrics & KPIs

| KPI | Definition | Target | Why It Matters |
|---|---|---|---|
| **Coverage Score** | actual_provider_hours / required_provider_hours | 0.95–1.10 | Below 0.85 = patient wait times spike; above 1.15 = labor waste |
| **Patients per Provider Hour** | total_patient_visits / actual_provider_hours | ≥ 2.5 | Core productivity metric — revenue is directly proportional |
| **Labor Cost per Visit** | total_labor_cost / total_patient_visits | ≤ regional benchmark | Profitability driver — the primary variable cost per patient encounter |
| **Overtime Rate** | overtime_hours / total_hours_worked | ≤ 8% | Indicator of chronic understaffing; also burnout risk signal |
| **Shift Gap Frequency** | shifts_with_gap / total_shifts | ≤ 10% | Availability risk — how often patients arrive to understaffed clinics |
| **Callout Rate** | callout_count / scheduled_shifts | ≤ 5% | Leading indicator of morale issues and impending coverage problems |
| **Avg Wait Time** | avg_wait_time_minutes per location | ≤ 25 min | Patient satisfaction proxy — directly affects NPS and return visits |
| **Fill Rate** | filled_budgeted_positions / total_budgeted_positions | ≥ 90% | Structural staffing health — are we keeping up with headcount targets? |

---

## 4. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM ARCHITECTURE                                    │
│                                                                              │
│  ┌────────────────────┐     ┌─────────────────────┐     ┌────────────────┐  │
│  │  Simulated HRIS    │     │   Python ETL         │     │   BigQuery     │  │
│  │  REST API          │────▶│   Cloud Function     │────▶│   Warehouse    │  │
│  │  (Cloud Run)       │     │                      │     │                │  │
│  │                    │     │  ┌─────────────────┐ │     │  Dimensions:   │  │
│  │  Endpoints:        │     │  │ 1. Extract      │ │     │  dim_employee  │  │
│  │  /workers          │     │  │ 2. Validate     │ │     │  dim_location  │  │
│  │  /schedules        │     │  │ 3. Transform    │ │     │  dim_job       │  │
│  │  /patient-volume   │     │  │ 4. Load         │ │     │  dim_date      │  │
│  │  /locations        │     │  └─────────────────┘ │     │                │  │
│  │  /terminations     │     │                      │     │  Facts:        │  │
│  │  /health           │     │  Quarantine tables   │     │  fact_daily_   │  │
│  │                    │     │  for failed records   │     │    staffing    │  │
│  └────────────────────┘     └──────────┬──────────┘     │  fact_shift_   │  │
│         ▲                              │                 │    gap         │  │
│         │                              │                 │                │  │
│  ┌────────────────────┐     ┌──────────▼──────────┐     │  Utility:      │  │
│  │  Faker + Seed      │     │  Cloud Scheduler     │     │  _pipeline_    │  │
│  │  Data Generators   │     │  (Daily 6AM UTC)     │     │    runs        │  │
│  │                    │     │                      │     │  _dq_log       │  │
│  └────────────────────┘     └─────────────────────┘     └───────┬────────┘  │
│                                                                  │           │
│                                                                  ▼           │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │  React Dashboard (Vercel)                                             │   │
│  │  ┌──────────┐ ┌──────────────┐ ┌───────────┐ ┌───────────────────┐   │   │
│  │  │  Hero /  │ │ Architecture │ │ Staffing  │ │  Data Quality +   │   │   │
│  │  │ Landing  │ │  Deep Dive   │ │ Dashboard │ │  SQL Showcase     │   │   │
│  │  └──────────┘ └──────────────┘ └───────────┘ └───────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │  Supporting: Cloud Storage (staging) · Cloud Logging · IAM · Secrets │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Summary

| Component | GCP Service | Purpose | Free Tier Coverage |
|---|---|---|---|
| Simulated HRIS API | Cloud Run | REST API returning realistic staffing data | 2M requests/month free |
| ETL Pipeline | Cloud Functions (2nd Gen) | Extract, validate, transform, load | 2M invocations/month free |
| Scheduler | Cloud Scheduler | Trigger daily pipeline runs | 3 jobs/month free |
| Data Warehouse | BigQuery | Star-schema analytics warehouse | 10GB storage + 1TB queries/month free |
| Staging Bucket | Cloud Storage | Temporary raw data staging | 5GB free |
| Dashboard | Vercel | Interactive portfolio + staffing analytics | Free tier |
| Source Code | GitHub | Version-controlled, documented repo | Free |

---

## 5. Simulated HRIS API Specification

**Purpose:** Mimic workforce and operational data sources that would exist in TAG's real environment (Workday HRIS, scheduling/timekeeping system, patient volume reporting). Returns realistic multi-location urgent care staffing data.

**Tech Stack:** Python 3.11+, FastAPI, Faker, Docker

### Endpoints

```
GET  /api/v1/workers
     → Paginated employee/clinician records
     Query params: ?page=1&page_size=100&location_id=LOC-042&role_type=Provider

GET  /api/v1/workers/{employee_id}
     → Single employee detail

GET  /api/v1/schedules
     → Scheduled and actual shift data by location and date range
     Query params: ?start_date=2026-01-01&end_date=2026-01-31&location_id=LOC-042

GET  /api/v1/patient-volume
     → Daily patient visit counts by location
     Query params: ?start_date=2026-01-01&end_date=2026-01-31&location_id=LOC-042

GET  /api/v1/locations
     → Location master data (all WellNow clinics)

GET  /api/v1/terminations
     → Termination records within a date range
     Query params: ?start_date=2025-01-01&end_date=2026-01-31

GET  /health
     → Health check / readiness probe
```

### Data Generation Requirements

- **Organization modeled:** ~80 urgent care clinic locations across 15 states, ~1,200 employees
- **Role types:** Provider (MD/DO/PA/NP), RN, Medical Assistant, Radiology Tech, Office Manager, Front Desk
- **Referential integrity:** Every employee → valid location; every manager_id → valid employee
- **Realistic distributions:**
  - ~22% annual attrition for support staff, ~12% for providers
  - Seasonal patient volume (higher in winter/flu season, lower in summer)
  - Day-of-week demand patterns (Monday and weekend peaks for urgent care)
  - Urban locations higher volume than rural; staffing ratios vary accordingly
  - 5–8% callout rate; overtime concentrated at understaffed locations
- **Historical depth:** 18 months of daily scheduling and patient volume data
- **Seed-based reproducibility:** Deterministic output for consistent demo and testing

### Authentication

API key via `X-API-Key` header (simulates enterprise API auth pattern). Key stored in environment variable, validated on every request.

---

## 6. ETL Pipeline Specification

**Purpose:** Production-grade ETL that extracts from the HRIS API, validates data quality, transforms into analytics-ready models, and loads into BigQuery.

**Tech Stack:** Python 3.11+, pandas, google-cloud-bigquery, google-cloud-storage, requests, pydantic

### Stage 1: Extract

```python
"""
Responsibilities:
- Authenticate with HRIS API using API key
- Paginate through all endpoints with configurable page_size
- Implement exponential backoff for rate limiting (max 3 retries)
- Handle API errors gracefully (timeouts, 5xx, malformed responses)
- Stage raw JSON responses to Cloud Storage as timestamped files
  Pattern: gs://{bucket}/raw/{endpoint}/{YYYY-MM-DD}/{timestamp}.json
- Log extraction metrics: records_fetched, duration_ms, errors, bytes
- Support both full and incremental extraction modes
"""
```

### Stage 2: Validate

```python
"""
Responsibilities:
- Schema validation using Pydantic models (strict mode)
- Execute all 15 data quality rules (see Section 8)
- Null checks on required fields
- Referential integrity checks (location_key exists, manager_id valid)
- Range validation (hours >= 0, patient_visits >= 0, coverage_score reasonable)
- Duplicate detection (composite key uniqueness)
- Flag but DO NOT drop invalid records → route to _quarantine table
- Generate structured DQ report: pass/fail counts per rule, per table
- Write results to _data_quality_log table in BigQuery
"""
```

### Stage 3: Transform

```python
"""
Responsibilities:
- Flatten nested JSON into tabular format
- Derive calculated fields:
    - coverage_score = actual_provider_hours / required_provider_hours
    - patients_per_provider_hour = patient_visits / actual_provider_hours
    - labor_cost_per_visit = total_labor_cost / patient_visits
    - overtime_rate = overtime_hours / total_hours_worked
    - gap_flag = TRUE when actual_providers < required_providers
    - excess_flag = TRUE when actual_providers > required_providers * 1.15
    - staffing_classification (Chronically Understaffed / Needs Attention /
      Optimally Staffed / Potentially Overstaffed) based on rolling coverage
    - tenure_band (0-1yr, 1-3yr, 3-5yr, 5-10yr, 10+yr)
    - is_new_hire (hired within last 90 days)
- Standardize fields (title case names, ISO dates, consistent enums)
- Build SCD Type 2 history for dim_employee (job/location changes)
- Aggregate shift-level data into fact_daily_staffing
- Detect shift gaps and populate fact_shift_gap
"""
```

### Stage 4: Load

```python
"""
Responsibilities:
- Write to BigQuery using load jobs (not streaming — cost optimization)
- WRITE_TRUNCATE for dimension tables (full refresh)
- WRITE_APPEND for fact tables (incremental)
- Partition fact tables by date for query performance and cost
- Cluster dimension tables by location and role_type
- Update _pipeline_runs metadata table
- Export dashboard-ready JSON to Cloud Storage (Option C for dashboard)
- Log load metrics: rows_loaded, duration, bytes_written
"""
```

### Configuration

```yaml
# config/pipeline.yaml
source:
  base_url: "${HRIS_API_URL}"
  api_key: "${HRIS_API_KEY}"
  page_size: 500
  max_retries: 3
  timeout_seconds: 30
  endpoints:
    - workers
    - schedules
    - patient-volume
    - locations
    - terminations

destination:
  project_id: "${GCP_PROJECT_ID}"
  dataset_id: "people_analytics"
  staging_bucket: "${GCS_STAGING_BUCKET}"
  dashboard_bucket: "${GCS_DASHBOARD_BUCKET}"

pipeline:
  run_mode: "full"  # or "incremental"
  lookback_days: 7
  enable_quarantine: true
  log_level: "INFO"

quality:
  fail_pipeline_on_critical: true
  warn_threshold: 0.95
  alert_threshold: 0.85
```

---

## 7. BigQuery Data Warehouse Schema

**Dataset:** `people_analytics`

### Dimension Tables

**`dim_employee`** (SCD Type 2)
```sql
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
  tenure_band         STRING,                -- Derived
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
```

**`dim_location`**
```sql
CREATE TABLE IF NOT EXISTS people_analytics.dim_location (
  location_key            INT64 NOT NULL,
  location_id             STRING NOT NULL,      -- LOC-XXX
  location_name           STRING NOT NULL,
  region                  STRING NOT NULL,
  state                   STRING NOT NULL,
  metro_area              STRING,
  location_type           STRING NOT NULL,       -- Urban, Suburban, Rural
  operating_hours_start   STRING,                -- e.g., "08:00"
  operating_hours_end     STRING,                -- e.g., "20:00"
  days_open_per_week      INT64,
  budgeted_provider_fte   FLOAT64,
  budgeted_support_fte    FLOAT64,
  opened_date             DATE,
  is_active               BOOL DEFAULT TRUE,
  _loaded_at              TIMESTAMP NOT NULL
)
CLUSTER BY region, state;
```

**`dim_job`**
```sql
CREATE TABLE IF NOT EXISTS people_analytics.dim_job (
  job_key         INT64 NOT NULL,
  job_title       STRING NOT NULL,
  role_type       STRING NOT NULL,     -- Provider, RN, MA, RadTech, OfficeMgr, FrontDesk
  job_level       STRING,
  is_clinical     BOOL,                -- TRUE for Provider, RN, MA, RadTech
  is_provider     BOOL,                -- TRUE for MD/DO/PA/NP only
  _loaded_at      TIMESTAMP NOT NULL
);
```

**`dim_date`**
```sql
CREATE TABLE IF NOT EXISTS people_analytics.dim_date (
  date_key        INT64 NOT NULL,       -- YYYYMMDD
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
```

### Fact Tables

**`fact_daily_staffing`** — Core staffing metrics per location per day
```sql
CREATE TABLE IF NOT EXISTS people_analytics.fact_daily_staffing (
  date_key                    INT64 NOT NULL,
  snapshot_date               DATE NOT NULL,
  location_key                INT64 NOT NULL,
  -- Provider staffing
  scheduled_provider_hours    FLOAT64,
  actual_provider_hours       FLOAT64,
  required_provider_hours     FLOAT64,       -- Based on patient demand model
  -- Support staff
  scheduled_support_hours     FLOAT64,
  actual_support_hours        FLOAT64,
  -- Operational
  overtime_hours              FLOAT64,
  callout_count               INT64,
  -- Patient volume
  patient_visits              INT64,
  -- Derived metrics (computed in transform)
  patients_per_provider_hour  FLOAT64,
  avg_wait_time_minutes       FLOAT64,
  coverage_score              FLOAT64,       -- actual / required
  labor_cost_total            FLOAT64,
  labor_cost_per_visit        FLOAT64,
  -- Metadata
  _loaded_at                  TIMESTAMP NOT NULL,
  _batch_id                   STRING
)
PARTITION BY snapshot_date
CLUSTER BY location_key;
```

**`fact_shift_gap`** — Shift-level understaffing/overstaffing detection
```sql
CREATE TABLE IF NOT EXISTS people_analytics.fact_shift_gap (
  date_key              INT64 NOT NULL,
  snapshot_date         DATE NOT NULL,
  location_key          INT64 NOT NULL,
  shift_window          STRING NOT NULL,     -- AM (8-12), PM (12-16), Evening (16-20)
  required_providers    INT64,
  scheduled_providers   INT64,
  actual_providers      INT64,
  gap_flag              BOOL,                -- TRUE when actual < required
  excess_flag           BOOL,                -- TRUE when actual > required * 1.15
  gap_hours             FLOAT64,             -- Hours of unfilled provider time
  excess_hours          FLOAT64,             -- Hours of excess provider time
  _loaded_at            TIMESTAMP NOT NULL,
  _batch_id             STRING
)
PARTITION BY snapshot_date
CLUSTER BY location_key, shift_window;
```

### Utility Tables

**`_pipeline_runs`**
```sql
CREATE TABLE IF NOT EXISTS people_analytics._pipeline_runs (
  run_id                STRING NOT NULL,
  pipeline_name         STRING NOT NULL,
  started_at            TIMESTAMP NOT NULL,
  completed_at          TIMESTAMP,
  status                STRING,             -- Success, Failed, Partial
  records_extracted     INT64,
  records_validated     INT64,
  records_quarantined   INT64,
  records_loaded        INT64,
  error_message         STRING,
  run_duration_seconds  FLOAT64,
  _batch_id             STRING
);
```

**`_data_quality_log`**
```sql
CREATE TABLE IF NOT EXISTS people_analytics._data_quality_log (
  check_date        DATE NOT NULL,
  check_name        STRING NOT NULL,
  table_name        STRING NOT NULL,
  check_type        STRING NOT NULL,
  records_checked   INT64,
  records_passed    INT64,
  records_failed    INT64,
  pass_rate         FLOAT64,
  severity          STRING NOT NULL,    -- Critical, High, Medium, Low
  status            STRING NOT NULL,    -- Pass, Warn, Fail
  details           STRING,
  _batch_id         STRING
);
```

**`_quarantine`** — Rejected records with error context
```sql
CREATE TABLE IF NOT EXISTS people_analytics._quarantine (
  quarantine_date     TIMESTAMP NOT NULL,
  source_table        STRING NOT NULL,
  record_json         STRING,           -- Original record as JSON string
  failure_rule_id     STRING,
  failure_reason      STRING,
  _batch_id           STRING
);
```

### Showcase SQL Queries

**Query 1: Location Staffing Efficiency Scorecard (Window Functions + CASE Classification)**
```sql
WITH location_metrics AS (
  SELECT
    l.location_name,
    l.region,
    l.state,
    l.location_type,
    DATE_TRUNC(ds.snapshot_date, WEEK(MONDAY)) AS week_start,
    AVG(ds.coverage_score) AS avg_coverage,
    SUM(ds.overtime_hours) AS total_overtime,
    AVG(ds.patients_per_provider_hour) AS avg_productivity,
    AVG(ds.avg_wait_time_minutes) AS avg_wait_time,
    SUM(ds.labor_cost_total) AS total_labor_cost,
    SUM(ds.patient_visits) AS total_visits,
    SAFE_DIVIDE(SUM(ds.labor_cost_total), NULLIF(SUM(ds.patient_visits), 0)) AS cost_per_visit
  FROM people_analytics.fact_daily_staffing ds
  JOIN people_analytics.dim_location l ON ds.location_key = l.location_key
  WHERE ds.snapshot_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY 1, 2, 3, 4, 5
),
location_summary AS (
  SELECT
    location_name,
    region,
    state,
    location_type,
    ROUND(AVG(avg_coverage), 3) AS avg_coverage_score,
    ROUND(AVG(avg_productivity), 2) AS avg_patients_per_provider_hr,
    ROUND(AVG(avg_wait_time), 1) AS avg_wait_minutes,
    ROUND(AVG(cost_per_visit), 2) AS avg_cost_per_visit,
    ROUND(SUM(total_overtime), 1) AS total_overtime_hours_90d,
    ROUND(SUM(total_visits), 0) AS total_visits_90d,
    ROUND(AVG(avg_coverage) - LAG(AVG(avg_coverage), 1) OVER (
      PARTITION BY location_name ORDER BY MAX(week_start)
    ), 3) AS coverage_trend_wow
  FROM location_metrics
  GROUP BY location_name, region, state, location_type
)
SELECT
  *,
  CASE
    WHEN avg_coverage_score < 0.85 THEN 'Chronically Understaffed'
    WHEN avg_coverage_score BETWEEN 0.85 AND 0.95 THEN 'Needs Attention'
    WHEN avg_coverage_score BETWEEN 0.95 AND 1.10 THEN 'Optimally Staffed'
    WHEN avg_coverage_score > 1.10 THEN 'Potentially Overstaffed'
  END AS staffing_classification,
  CASE
    WHEN coverage_trend_wow > 0.02 THEN 'Improving'
    WHEN coverage_trend_wow < -0.02 THEN 'Declining'
    ELSE 'Stable'
  END AS trend_direction
FROM location_summary
ORDER BY avg_coverage_score ASC;
```

**Query 2: Shift Gap Analysis with Float Clinician Deployment Recommendations (CTEs + DENSE_RANK)**
```sql
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
    WHEN regional_priority <= 3 THEN 'URGENT — Deploy Float Immediately'
    WHEN regional_priority <= 7 THEN 'HIGH — Schedule Float Coverage'
    ELSE 'MONITOR — Track for Escalation'
  END AS recommended_action
FROM ranked_needs
WHERE regional_priority <= 15
ORDER BY region, regional_priority;
```

**Query 3: Overtime Hotspot Analysis & Labor Cost Impact (Aggregation + Running Totals)**
```sql
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
    WHEN overtime_rate > regional_avg_ot_rate * 1.5 THEN 'Critical — Significantly Above Regional Avg'
    WHEN overtime_rate > regional_avg_ot_rate * 1.2 THEN 'Elevated — Above Regional Avg'
    ELSE 'Normal'
  END AS overtime_alert_level
FROM with_benchmarks
WHERE month >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
ORDER BY overtime_rate DESC;
```

---

## 8. Data Quality Framework

### Validation Rules

| Rule ID | Check Type | Table | Rule | Severity | Action on Failure |
|---|---|---|---|---|---|
| DQ-001 | Null Check | dim_employee | employee_id IS NOT NULL | Critical | Quarantine record |
| DQ-002 | Null Check | dim_employee | hire_date IS NOT NULL | Critical | Quarantine record |
| DQ-003 | Null Check | dim_employee | role_type IS NOT NULL | Critical | Quarantine record |
| DQ-004 | Uniqueness | dim_employee | employee_id unique per is_current=TRUE | Critical | Quarantine duplicate |
| DQ-005 | Referential | dim_employee | location_key EXISTS in dim_location | High | Quarantine record |
| DQ-006 | Referential | dim_employee | manager_employee_id EXISTS in employee set (or NULL for top-level) | High | Flag, allow through |
| DQ-007 | Range | fact_daily_staffing | patient_visits >= 0 | High | Quarantine record |
| DQ-008 | Range | fact_daily_staffing | coverage_score BETWEEN 0 AND 3.0 | Medium | Flag, allow through |
| DQ-009 | Range | fact_daily_staffing | overtime_hours >= 0 AND <= 24 | High | Quarantine record |
| DQ-010 | Consistency | dim_employee | IF status='Active' THEN termination_date IS NULL | High | Flag, allow through |
| DQ-011 | Consistency | dim_employee | IF status='Terminated' THEN termination_date IS NOT NULL | High | Flag, allow through |
| DQ-012 | Freshness | fact_daily_staffing | MAX(snapshot_date) within 2 days of CURRENT_DATE | Critical | Alert |
| DQ-013 | Volume | dim_employee | Row count within 10% of previous run | High | Alert |
| DQ-014 | Format | dim_employee | email LIKE '%@wellnow.com' | Low | Flag, allow through |
| DQ-015 | Cross-table | fact_daily_staffing | Every active location in dim_location has ≥1 staffing record per day | Medium | Alert |

### Quality Scoring

```
Overall DQ Score = (Critical Pass Rate × 0.40)
                 + (High Pass Rate × 0.30)
                 + (Medium Pass Rate × 0.20)
                 + (Low Pass Rate × 0.10)

Thresholds:
  ≥ 95%  → ✅ Healthy
  ≥ 85%  → ⚠️ Warning
  < 85%  → 🔴 Alert — pipeline may produce unreliable analytics
```

---

## 9. Dashboard Specification

**Tech Stack:** React 18+, Vite, Tailwind CSS, Recharts, React Router
**Hosting:** Vercel (free tier)
**Data Layer:** Pre-computed JSON files in Cloud Storage (Option C — simplest, cheapest, most reliable for POC)

### Page 1: Hero / Landing

- Candidate name: **Kriti Srivastava**
- Title: *"People Analytics Engineer — Workforce Optimization"*
- Positioning: *"I built a live data pipeline that turns HRIS and scheduling data into actionable staffing intelligence for multi-location healthcare operations — the same infrastructure this role requires."*
- Animated architecture diagram
- Key stats: *"1,200 employees · 80 locations · 18 months of data · 15 validation rules · 3 showcase queries"*
- CTAs: "View Staffing Dashboard" · "View GitHub" · "View Architecture"

### Page 2: Architecture Deep Dive

- Interactive pipeline diagram (click components for details)
- Component cards: tech stack, purpose, code snippet preview
- Data flow animation
- Cost breakdown: $0/month on GCP free tier

### Page 3: Staffing Optimization Dashboard (Primary)

**KPI Cards (top row):**
- Avg Coverage Score (with trend arrow)
- Total Overtime Hours (30d)
- Avg Cost Per Visit (with regional benchmark)
- Shift Gap Rate (% of shifts understaffed)
- Avg Patient Wait Time
- Fill Rate (% of budgeted positions filled)

**Visualizations:**
1. **Staffing Coverage Map** — Geographic bubble chart: locations sized by patient volume, colored by coverage_score (red/yellow/green)
2. **Understaffing Hot Spots** — Heatmap matrix: Location (y-axis) × Day-of-Week (x-axis), cell color = gap_frequency
3. **Labor Cost Per Visit Trend** — Multi-line time series by region, with target benchmark line
4. **Overtime Waterfall** — Horizontal bar chart: top 15 locations by overtime hours, colored by alert level
5. **Float Deployment Planner** — Sortable table: recommended float assignments with priority, location, shift, gap hours

**Interactivity:**
- Date range selector (last 30d / 90d / 6mo / 12mo)
- Region filter dropdown
- Location type filter (Urban / Suburban / Rural)

### Page 4: Data Quality Monitor

- Pipeline run history table (last 30 runs: status, duration, record counts)
- DQ scorecard by rule severity (Critical/High/Medium/Low pass rates)
- Freshness indicator (time since last successful load)
- DQ trend chart over time

### Page 5: SQL Showcase

- 3 featured queries with syntax highlighting (Prism.js or similar)
- Each query: business question → SQL code → sample results table → explanation
- Toggle between "Query" and "Results" views

### Page 6: How I Built This

- AI-assisted development workflow narrative
- Time breakdown by phase
- Lessons learned and trade-offs
- Link to GitHub repository

---

## 10. Enterprise File Structure & Repository Layout

The repository follows enterprise-grade conventions for a healthcare data platform: clear separation of concerns, configuration externalized from code, secrets management patterns, compliance-aware documentation, and CI-ready structure.

```
wellnow-staffing-analytics/
│
├── README.md                              # Project overview, architecture diagram, quickstart
├── LICENSE                                # MIT License
├── CONTRIBUTING.md                        # Contribution guidelines
├── CHANGELOG.md                           # Version history
├── .gitignore                             # Python, Node, GCP, IDE exclusions
├── .env.example                           # Template for environment variables (NO secrets)
├── Makefile                               # Common commands (setup, test, lint, deploy)
│
├── .github/                               # CI/CD & GitHub configuration
│   ├── workflows/
│   │   ├── ci.yml                         # Lint + test on every PR
│   │   ├── deploy-api.yml                 # Deploy HRIS API to Cloud Run
│   │   └── deploy-etl.yml                 # Deploy ETL to Cloud Functions
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
│
├── docs/                                  # Enterprise documentation
│   ├── architecture.md                    # Detailed architecture writeup & diagrams
│   ├── data_dictionary.md                 # Field-level documentation for every table
│   ├── data_lineage.md                    # Source → transform → destination mapping
│   ├── data_quality_runbook.md            # DQ monitoring & incident response
│   ├── runbook.md                         # Operational procedures (deploy, rollback, debug)
│   ├── api_specification.md               # OpenAPI-style endpoint documentation
│   ├── security_and_compliance.md         # HIPAA, data privacy, access control documentation
│   └── ai_development_log.md             # AI-assisted development notes
│
├── src/                                   # Application source code
│   │
│   ├── api/                               # Simulated HRIS API (Cloud Run service)
│   │   ├── Dockerfile                     # Multi-stage build for production
│   │   ├── .dockerignore
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt           # Test + lint dependencies
│   │   ├── main.py                        # FastAPI application entry point
│   │   ├── config.py                      # API configuration (env-based)
│   │   ├── auth.py                        # API key authentication middleware
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── workers.py                 # /api/v1/workers endpoints
│   │   │   ├── schedules.py               # /api/v1/schedules endpoint
│   │   │   ├── patient_volume.py          # /api/v1/patient-volume endpoint
│   │   │   ├── locations.py               # /api/v1/locations endpoint
│   │   │   ├── terminations.py            # /api/v1/terminations endpoint
│   │   │   └── health.py                  # /health endpoint
│   │   ├── models/                        # Pydantic request/response models
│   │   │   ├── __init__.py
│   │   │   ├── employee.py
│   │   │   ├── schedule.py
│   │   │   ├── patient_volume.py
│   │   │   ├── location.py
│   │   │   └── common.py                  # Shared types (pagination, errors)
│   │   ├── generators/                    # Faker-based realistic data generation
│   │   │   ├── __init__.py
│   │   │   ├── seed.py                    # Master seed & reproducibility
│   │   │   ├── organization.py            # Location & org structure generation
│   │   │   ├── employee_generator.py      # Employee/clinician records
│   │   │   ├── schedule_generator.py      # Shift schedules & actuals
│   │   │   ├── patient_volume_generator.py # Daily patient visit patterns
│   │   │   └── termination_generator.py   # Attrition events
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── conftest.py                # Shared fixtures
│   │       ├── test_api_workers.py
│   │       ├── test_api_schedules.py
│   │       ├── test_api_patient_volume.py
│   │       ├── test_api_locations.py
│   │       ├── test_generators.py
│   │       └── test_auth.py
│   │
│   ├── etl/                               # ETL Pipeline (Cloud Functions)
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   ├── main.py                        # Cloud Function entry point (HTTP trigger)
│   │   ├── pipeline.py                    # Pipeline orchestrator
│   │   ├── extract.py                     # API extraction with pagination & retries
│   │   ├── validate.py                    # Data quality checks (15 rules)
│   │   ├── transform.py                   # Transformations & derived fields
│   │   ├── load.py                        # BigQuery writer
│   │   ├── export_dashboard_data.py       # Export analytics JSON for dashboard
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.yaml              # Pipeline configuration
│   │   │   └── settings.py                # Config loader with env var support
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py                 # Pydantic validation schemas
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py                  # Structured logging (JSON format)
│   │   │   ├── retry.py                   # Exponential backoff decorator
│   │   │   ├── metrics.py                 # Pipeline run metrics collector
│   │   │   └── gcp.py                     # GCP client helpers (BQ, GCS)
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_extract.py
│   │       ├── test_validate.py
│   │       ├── test_transform.py
│   │       ├── test_load.py
│   │       └── test_pipeline_integration.py
│   │
│   └── dashboard/                         # React Dashboard (Vercel)
│       ├── package.json
│       ├── package-lock.json
│       ├── vite.config.js
│       ├── tailwind.config.js
│       ├── postcss.config.js
│       ├── index.html
│       ├── vercel.json                    # Vercel deployment config
│       ├── public/
│       │   ├── favicon.ico
│       │   └── data/                      # Pre-computed JSON (Option C)
│       │       ├── kpis.json
│       │       ├── staffing_coverage.json
│       │       ├── shift_gaps.json
│       │       ├── overtime_hotspots.json
│       │       ├── labor_cost_trends.json
│       │       ├── pipeline_runs.json
│       │       └── dq_scores.json
│       └── src/
│           ├── App.jsx
│           ├── main.jsx
│           ├── routes.jsx                 # React Router config
│           ├── pages/
│           │   ├── Hero.jsx
│           │   ├── Architecture.jsx
│           │   ├── StaffingDashboard.jsx  # Primary analytics page
│           │   ├── DataQuality.jsx
│           │   ├── SQLShowcase.jsx
│           │   └── HowIBuiltThis.jsx
│           ├── components/
│           │   ├── layout/
│           │   │   ├── Navigation.jsx
│           │   │   ├── Footer.jsx
│           │   │   └── PageContainer.jsx
│           │   ├── dashboard/
│           │   │   ├── KPICard.jsx
│           │   │   ├── CoverageMap.jsx
│           │   │   ├── GapHeatmap.jsx
│           │   │   ├── LaborCostTrend.jsx
│           │   │   ├── OvertimeWaterfall.jsx
│           │   │   ├── FloatDeploymentTable.jsx
│           │   │   └── DateRangeFilter.jsx
│           │   ├── quality/
│           │   │   ├── PipelineRunsTable.jsx
│           │   │   ├── DQScorecard.jsx
│           │   │   └── FreshnessIndicator.jsx
│           │   ├── showcase/
│           │   │   ├── SQLBlock.jsx
│           │   │   └── ResultsTable.jsx
│           │   └── architecture/
│           │       └── PipelineDiagram.jsx
│           ├── hooks/
│           │   └── useDataLoader.js       # Custom hook for JSON data fetching
│           ├── utils/
│           │   ├── formatters.js          # Number, date, currency formatting
│           │   └── constants.js           # KPI thresholds, colors, labels
│           └── styles/
│               └── globals.css
│
├── sql/                                   # BigQuery SQL (version-controlled)
│   ├── schema/
│   │   ├── 001_create_dataset.sql
│   │   ├── 002_create_dim_employee.sql
│   │   ├── 003_create_dim_location.sql
│   │   ├── 004_create_dim_job.sql
│   │   ├── 005_create_dim_date.sql
│   │   ├── 006_create_fact_daily_staffing.sql
│   │   ├── 007_create_fact_shift_gap.sql
│   │   ├── 008_create_utility_tables.sql
│   │   └── 009_create_quarantine.sql
│   ├── seed/
│   │   └── seed_dim_date.sql
│   ├── queries/                           # Showcase analytics queries
│   │   ├── staffing_efficiency_scorecard.sql
│   │   ├── shift_gap_float_deployment.sql
│   │   └── overtime_hotspot_analysis.sql
│   └── migrations/                        # Schema evolution (future)
│       └── .gitkeep
│
├── infrastructure/                        # Deployment & IaC scripts
│   ├── scripts/
│   │   ├── setup_gcp_project.sh           # Initial GCP project config
│   │   ├── deploy_api.sh                  # Cloud Run deploy
│   │   ├── deploy_etl.sh                  # Cloud Functions deploy
│   │   ├── setup_scheduler.sh             # Cloud Scheduler job creation
│   │   ├── setup_bigquery.sh              # Run schema SQL scripts
│   │   ├── setup_secrets.sh               # Secret Manager configuration
│   │   └── teardown.sh                    # Full cleanup script
│   └── config/
│       ├── cloud_run.yaml                 # Cloud Run service config
│       ├── cloud_function.yaml            # Cloud Function config
│       └── billing_alerts.json            # Budget alert configuration
│
├── config/                                # Shared configuration
│   ├── .env.example                       # Environment variable template
│   ├── logging.yaml                       # Logging configuration
│   └── quality_rules.yaml                 # DQ rule definitions (externalized)
│
└── scripts/                               # Developer utility scripts
    ├── generate_sample_data.py            # Local data generation for dev/test
    ├── run_quality_checks.py              # Run DQ rules locally
    ├── export_dashboard_json.py           # Manual dashboard JSON export
    └── validate_schema.py                 # Schema drift detection
```

### File Structure Design Principles

| Principle | Implementation |
|---|---|
| **Separation of concerns** | `src/api/`, `src/etl/`, `src/dashboard/` are independently deployable units |
| **Configuration externalized** | All config in `config/` or env vars; zero hardcoded secrets |
| **SQL version-controlled** | Numbered migration-style schema files in `sql/schema/` |
| **Tests co-located** | Each `src/` module has its own `tests/` directory |
| **Documentation first-class** | `docs/` is comprehensive; not an afterthought |
| **CI/CD ready** | `.github/workflows/` with lint + test + deploy pipelines |
| **Compliance artifacts** | `docs/security_and_compliance.md` documents HIPAA-relevant decisions |
| **Reproducible builds** | Pinned `requirements.txt`, lockfiles, Dockerfile with multi-stage build |

---

## 11. Security, Privacy & Compliance

This POC uses **100% synthetic data** — no real patient data, no real employee PII, no PHI. However, the architecture and code patterns are designed as if real data were flowing through the system, demonstrating awareness of healthcare compliance requirements.

### HIPAA Considerations (Demonstrated in Architecture)

| HIPAA Requirement | How POC Addresses It |
|---|---|
| **Minimum Necessary Rule** | API returns only fields required for analytics — no SSN, DOB, medical records |
| **Access Control** | API key authentication on every endpoint; IAM-based BigQuery access |
| **Audit Logging** | `_pipeline_runs` and `_data_quality_log` tables create a complete audit trail of every data access and transformation |
| **Encryption at Rest** | BigQuery and Cloud Storage encrypt at rest by default (Google-managed keys) |
| **Encryption in Transit** | All API calls over HTTPS; Cloud Run enforces TLS |
| **Data Retention** | Fact table partitioning enables time-based data lifecycle management |
| **Business Associate Agreement** | Noted as required for production (GCP provides BAA for healthcare customers) |

### Data Privacy Patterns (Demonstrated in Code)

| Pattern | Implementation |
|---|---|
| **No real PII in repository** | `.env.example` with placeholder values; `.gitignore` excludes `.env`, credentials, and data files |
| **Synthetic data only** | Faker-generated names, emails, IDs — clearly fictional |
| **Secret management** | API keys in environment variables; `setup_secrets.sh` documents Secret Manager pattern |
| **No credentials in code** | Zero hardcoded API keys, project IDs, or service account keys anywhere in source |
| **Quarantine pattern** | Invalid/suspicious records isolated in `_quarantine` table, not silently dropped or mixed into clean data |

### Additional Compliance Awareness

| Standard | Relevance | POC Approach |
|---|---|---|
| **SOC 2 Type II** | TAG likely undergoes SOC 2 audits as a healthcare platform | Audit trail tables, access controls, change management via Git |
| **CCPA / State Privacy** | TAG operates in 48 states including California | Data minimization principle; no unnecessary PII fields |
| **EEOC / Pay Equity** | Relevant for future Use Case 3 (out of scope for v1) | Schema supports demographic fields for future equity analysis |
| **OSHA / Labor Law** | Overtime tracking and workload monitoring | Overtime rate and shift gap metrics support labor compliance monitoring |

### `.gitignore` Must-Haves

```gitignore
# Secrets — NEVER commit
.env
.env.local
.env.production
*.key
*.pem
service-account*.json
credentials*.json

# Data files — NEVER commit raw data
*.csv
*.json.gz
data/raw/
data/staging/

# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# Node
node_modules/
dist/
.vercel/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# GCP
.gcloud/
```

---

## 12. Development Phases

### Phase 1: Architecture & Foundation (Day 1–2)

- [ ] Create GitHub repository with enterprise file structure
- [ ] Set up GCP project with $5 billing alert
- [ ] Create BigQuery dataset and all tables (run `sql/schema/` scripts)
- [ ] Seed `dim_date` table (2 years of dates)
- [ ] Seed `dim_location` table (80 urgent care clinics)
- [ ] Build simulated HRIS API locally (FastAPI + Faker)
  - [ ] All 6 endpoints with Pydantic models
  - [ ] Data generators with healthcare-realistic distributions
  - [ ] API key authentication middleware
  - [ ] Unit tests (>80% coverage on generators)
- [ ] Create Dockerfile and deploy API to Cloud Run
- [ ] Write `docs/architecture.md` and `docs/data_dictionary.md`

### Phase 2: ETL Pipeline (Day 3–4)

- [ ] Build extraction module with pagination and exponential backoff
- [ ] Build validation module with all 15 DQ rules
- [ ] Build transformation module with all derived fields
- [ ] Build load module with BigQuery schema handling
- [ ] Build `export_dashboard_data.py` for JSON output
- [ ] Integration test: full pipeline locally against Cloud Run API
- [ ] Deploy to Cloud Functions
- [ ] Set up Cloud Scheduler (daily 6AM UTC)
- [ ] First successful automated pipeline run
- [ ] Verify `_pipeline_runs` and `_data_quality_log` tables populated

### Phase 3: Dashboard (Day 5–6)

- [ ] Scaffold React app (Vite + Tailwind + React Router + Recharts)
- [ ] Hero / Landing page with architecture animation
- [ ] Architecture Deep Dive page
- [ ] Staffing Optimization Dashboard (all 5 visualizations + KPI cards + filters)
- [ ] Data Quality Monitor page
- [ ] SQL Showcase page (3 queries with highlighting + results)
- [ ] How I Built This page
- [ ] Mobile responsiveness pass
- [ ] Deploy to Vercel

### Phase 4: Polish & Documentation (Day 7)

- [ ] README with architecture diagram, quickstart, demo link
- [ ] Complete `docs/data_lineage.md`
- [ ] Complete `docs/security_and_compliance.md`
- [ ] Complete `docs/runbook.md`
- [ ] CI workflow: lint (ruff/black) + test (pytest) on PR
- [ ] Performance audit (Lighthouse score >90)
- [ ] Final code review pass: docstrings, type hints, naming consistency
- [ ] Update `CHANGELOG.md`

---

## 13. Cost Budget

| Service | Monthly Usage | Free Tier | Estimated Cost |
|---|---|---|---|
| BigQuery Storage | ~50 MB | 10 GB free | $0.00 |
| BigQuery Queries | ~5 GB/month | 1 TB free | $0.00 |
| Cloud Run (API) | ~100 requests/day | 2M requests free | $0.00 |
| Cloud Functions (ETL) | 1 run/day | 2M invocations free | $0.00 |
| Cloud Scheduler | 1 job | 3 jobs free | $0.00 |
| Cloud Storage | ~50 MB staging | 5 GB free | $0.00 |
| Vercel (Dashboard) | Static site | Free tier | $0.00 |
| GitHub | Public repo | Free | $0.00 |
| **Total** | | | **$0/month** |

**Safety Measures:**
- GCP billing alert at $5
- BigQuery daily scan limit: 1 GB
- Cloud Run max instances: 1
- Cloud Function timeout: 540s, memory: 512MB

---

## 14. Skills Demonstrated → Job Requirements Mapping

| TAG Job Requirement (verbatim from JD) | Where Demonstrated in POC |
|---|---|
| *"Supporting the WellNow brand through development of a common approach and infrastructure to data sources built to support enterprise-wide reporting"* | Entire project: star-schema BigQuery warehouse serving staffing analytics across 80 WellNow locations with standardized KPI definitions |
| *"Capture and translate business requirements for reporting from executive leadership"* | Section 3: stakeholder map translating exec needs into specific KPIs, queries, and dashboard views |
| *"Developing key data sources in BigQuery through use of SQL"* | Section 7: full schema design; 3 showcase queries with CTEs, window functions, DENSE_RANK |
| *"Synthesizing insights from various data sources and presenting data in an easy-to-read manner"* | Combining HRIS + scheduling + patient volume into unified staffing intelligence; dashboard with geographic maps, heatmaps, trend charts |
| *"Become organizational expert on data sources and how to extract data from all systems"* | `docs/data_dictionary.md`, `docs/data_lineage.md`, API specification, complete schema docs |
| *"Ability to combine multiple data sources; strong attention to detail and data integrity"* | 15 DQ validation rules, quarantine tables, audit trail in `_pipeline_runs`, referential integrity checks |
| *"Work across departments to understand how their work impacts the performance of the business deriving metrics to measure results"* | Coverage score links Operations → Patient Experience; labor cost per visit links HR → Finance; overtime rate links Staffing → Employee Wellbeing |
| *"Identify key opportunities to drive transparency and turn data into insights and action"* | Float Deployment Planner: not just "what happened" but "where to deploy resources next week" |
| *"Leading organization in implementing a standardized, consistent approach to reporting, with a strong focus on user experience to drive usage"* | Unified KPI definitions, consistent metric calculations across 80 locations, interactive dashboard with filters and drill-downs |
| *"Utilizing data to uncover trends and insights, connecting changes in operational metrics to broader business performance, and craft compelling narratives"* | Overtime Hotspot Analysis connects staffing gaps → overtime spend → cost per visit → per-location profitability |
| *"Experience writing in SQL or BigQuery"* | 3 showcase queries demonstrating CTEs, window functions, SAFE_DIVIDE, DENSE_RANK, CASE classification, DATE functions |
| *"Experience using data visualization software like Tableau or PowerBI"* | React dashboard with Recharts demonstrates data viz competency; translatable to Tableau/PowerBI |
| *"Ability to find and query appropriate data from databases, along with validating and reviewing data and reports for accuracy and completion"* | Full DQ framework, schema validation, data quality monitoring dashboard |
| *"Experience managing cross-functional projects with multiple stakeholders"* | PRD structure demonstrates cross-functional requirements gathering across Operations, Finance, HR, Recruiting |

---

## 15. Out of Scope (v1)

### Deferred Use Cases

| Use Case | Priority Score | Rationale for Deferral | Recommended For |
|---|---|---|---|
| **UC-1: Multi-Brand Clinician Retention & Attrition Intelligence** | 2.75 | High value but addresses workforce stability as a second-order effect. Requires cross-brand data model complexity that dilutes WellNow-specific focus. | **v2** |
| **UC-3: Compensation Competitiveness & Pay Equity Analytics** | 1.75 | Important for long-term talent strategy but minimal direct impact on patient-facing operations or per-location economics. Requires market benchmark data modeling. | **v3** |

### Deferred Technical Scope

- Real Workday / Cornerstone OnDemand integration (simulated instead)
- Real patient volume data or PHI of any kind
- User authentication / RBAC on the dashboard
- Real-time streaming (batch ETL is appropriate for daily staffing analytics cadence)
- dbt for transformations (raw Python demonstrates fundamentals more visibly)
- Terraform / IaC for infrastructure (shell scripts for POC simplicity)
- Multi-environment setup (dev / staging / prod)
- Row-level security in BigQuery
- ML-based demand forecasting for patient volume prediction
- Real-time alerting (Cloud Monitoring → PagerDuty/Slack)
- API rate limiting beyond simple API key auth
- CultureAmp or employee engagement survey integration
- Multi-brand cross-portfolio reporting (v1 is WellNow-only focus)

---

## 16. Claude Code Implementation Instructions

This section provides structured instructions for using Claude Code to implement this POC. The PRD must be provided as project context at the start of each Claude Code session.

---

### STEP 0: Architecture Design Phase (MANDATORY — Run Before Any Code)

> **CRITICAL INSTRUCTION:** Claude Code must complete the full architecture design phase before writing any application logic. This ensures design coherence across all components and prevents rework.

```
PROMPT — ARCHITECTURE DESIGN (START HERE):

You are implementing a People Analytics pipeline POC for WellNow Urgent Care
staffing optimization. The full PRD is available in this project's context
(PRD_People_Analytics_Healthcare_TAG.md).

BEFORE writing any application code, complete these architecture deliverables:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0A: Read & Internalize the PRD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Read Sections 1-15 of the PRD thoroughly. Confirm you understand:
- The business problem (Section 3)
- All 8 KPIs and their definitions
- The full BigQuery schema (Section 7) — every table, every field
- All 15 DQ rules (Section 8)
- The 3 showcase SQL queries
- The dashboard specification (Section 9)
- The file structure (Section 10)
- The compliance requirements (Section 11)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0B: Create the Full Repository Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Create EVERY directory, __init__.py, and .gitkeep file exactly as specified
in Section 10. Also create:
- .gitignore (from Section 11)
- .env.example with all required environment variables (placeholder values)
- Makefile with targets: setup, test, lint, deploy-api, deploy-etl, deploy-dashboard
- LICENSE (MIT)
- CONTRIBUTING.md (basic template)
- CHANGELOG.md (v0.1.0 — initial structure)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0C: Write Architecture Documentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Create these docs BEFORE any application code:

1. docs/architecture.md
   - System architecture with Mermaid diagram
   - Component interaction: API → ETL → BigQuery → Dashboard
   - Data flow: source → staging → warehouse → dashboard JSON
   - Technology choices with rationale for each
   - Deployment topology (Cloud Run, Cloud Functions, Vercel)
   - Error handling strategy (retries, quarantine, alerting)
   - What would change at TAG's scale (1,400 locations vs. 80)

2. docs/data_dictionary.md
   - Every table, every field: name, type, nullable, description, example
   - Business definition for every derived field
   - Source system origin for every raw field

3. docs/data_lineage.md
   - API endpoint → raw staging → BigQuery table → dashboard JSON
   - Every derived field: formula, input fields, transformation logic
   - Data freshness expectations per table

4. docs/security_and_compliance.md
   - Synthetic data declaration
   - Authentication patterns (API key, IAM)
   - Secret management approach (.env → Secret Manager for prod)
   - Audit trail design (_pipeline_runs, _dq_log)
   - HIPAA considerations (documented even though synthetic)
   - What changes for production with real PHI/PII

5. docs/api_specification.md
   - Every endpoint: method, path, params, response schema, examples
   - Authentication details
   - Error response format
   - Pagination spec

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0D: Create BigQuery Schema Files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Create all SQL files in sql/schema/ (001-009) exactly as specified in
Section 7 of the PRD. Also create:
- sql/seed/seed_dim_date.sql (2 years: 2025-01-01 to 2026-12-31)
- sql/queries/ — all 3 showcase queries from Section 7

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0E: Create config/quality_rules.yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Externalize all 15 DQ rules from Section 8 into a YAML file that the
ETL validate.py module will read. Each rule should have:
- rule_id, check_type, table_name, rule_definition, severity, action

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0F: Architecture Review Checklist
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Before proceeding to Phase 1, verify:
□ Can api/, etl/, dashboard/ each be deployed independently?
□ Are there ANY hardcoded values that should be in config/env vars?
□ Is every secret in .env.example (not in source code)?
□ Does .gitignore cover all sensitive files?
□ Would a reviewer understand the entire project from README + docs/?
□ Do all SQL files parse correctly?
□ Does quality_rules.yaml contain all 15 rules?

Confirm completion of Step 0 before proceeding to Phase 1.
```

---

### STEP 1: Foundation — Simulated HRIS API (Phase 1)

```
PROMPT — PHASE 1 IMPLEMENTATION:

Architecture design is complete. Now implement Phase 1 per the PRD:

Build the FastAPI application in src/api/:

1. main.py — FastAPI app with:
   - CORS middleware
   - Request/response logging middleware
   - Global exception handler with structured error responses
   - API version prefix (/api/v1)

2. auth.py — API key middleware:
   - Read key from HRIS_API_KEY env var
   - Validate X-API-Key header on every request except /health
   - Return 401 with structured error if invalid

3. config.py — Environment-based configuration:
   - All settings from env vars with sensible defaults
   - Pydantic Settings class for validation

4. Routers (src/api/routers/) — Each endpoint per Section 5:
   - workers.py: paginated list + single detail
   - schedules.py: date range + location filtered
   - patient_volume.py: date range + location filtered
   - locations.py: full location list
   - terminations.py: date range filtered
   - health.py: readiness check

5. Models (src/api/models/) — Pydantic v2 strict mode:
   - employee.py: EmployeeResponse, EmployeeListResponse
   - schedule.py: ShiftRecord, ScheduleResponse
   - patient_volume.py: DailyVolumeRecord, VolumeResponse
   - location.py: LocationResponse
   - common.py: PaginationMeta, ErrorResponse, APIKeyHeader

6. Generators (src/api/generators/) — CRITICAL for realism:
   - seed.py: MASTER_SEED = 42, deterministic Faker instances
   - organization.py: 80 locations across 15 states
     * Follow WellNow's geographic footprint: Northeast + Midwest heavy
     * Mix of Urban (40%), Suburban (45%), Rural (15%)
     * Each location has budgeted FTEs based on type
   - employee_generator.py: ~1,200 employees
     * Role distribution: 20% Provider, 15% RN, 25% MA, 10% RadTech,
       10% OfficeMgr, 20% FrontDesk
     * Tenure: right-skewed distribution (many new, few very long)
     * Attrition: 22% support, 12% provider annual rates
   - schedule_generator.py: 18 months of daily shift data
     * 3 shifts per location per day (AM/PM/Evening)
     * Seasonal patient demand patterns
     * Realistic callout rates (5-8%), higher on weekends
     * Overtime clustered at chronically understaffed locations
   - patient_volume_generator.py: correlated with season + staffing
     * Winter peaks (Nov-Feb), summer troughs (Jun-Aug)
     * Monday + Saturday peaks for urgent care
     * Urban > Suburban > Rural volumes
   - termination_generator.py: exit events with reason distribution

7. Tests (src/api/tests/):
   - test_generators.py: verify distributions, referential integrity,
     reproducibility across runs
   - test_api_*.py: endpoint response schemas, pagination, filtering
   - test_auth.py: valid key, invalid key, missing key

8. Dockerfile — Multi-stage build:
   - Stage 1: builder (install deps)
   - Stage 2: runtime (slim image, non-root user)
   - HEALTHCHECK instruction

QUALITY REQUIREMENTS:
- Type hints on EVERY function parameter and return value
- Docstrings on EVERY public function, class, and module
- No hardcoded values — everything from config.py
- Structured JSON logging via utils
- All Pydantic models in strict mode
```

---

### STEP 2: ETL Pipeline (Phase 2)

```
PROMPT — PHASE 2 IMPLEMENTATION:

API is working. Now build the ETL pipeline in src/etl/ per PRD Section 6:

1. main.py — Cloud Function HTTP entry point
2. pipeline.py — Orchestrator with run_id, stage tracking, metadata logging
3. extract.py — Paginated API calls with exponential backoff (utils/retry.py)
4. validate.py — All 15 DQ rules loaded from config/quality_rules.yaml
5. transform.py — All derived fields from Section 6 Stage 3
6. load.py — BigQuery load jobs, TRUNCATE dims / APPEND facts
7. export_dashboard_data.py — Run showcase queries, export JSON to GCS
8. config/settings.py — Load pipeline.yaml with env var interpolation
9. models/schemas.py — Pydantic validation schemas for each data entity
10. utils/ — logger.py, retry.py, metrics.py, gcp.py

Test the full pipeline locally: python -m src.etl.pipeline
Verify all BigQuery tables populated and _pipeline_runs shows Success.
```

---

### STEP 3: Dashboard (Phase 3)

```
PROMPT — PHASE 3 IMPLEMENTATION:

Pipeline is running. Build the React dashboard in src/dashboard/ per Section 9:

1. Scaffold: Vite + React 18 + Tailwind CSS + React Router v6 + Recharts
2. All 6 pages as specified in Section 9
3. StaffingDashboard.jsx is the PRIMARY page — it must be exceptional:
   - 6 KPI cards with trend indicators
   - 5 visualizations (map, heatmap, trend lines, waterfall, table)
   - 3 interactive filters (date range, region, location type)
4. Professional healthcare-appropriate color palette
5. Mobile responsive (tablet-friendly for field ops)
6. Sample JSON data in public/data/ for development
7. Deploy to Vercel

DESIGN: Clean, professional, data-dense but not cluttered. Think
Tableau/PowerBI dashboard quality, not a toy demo.
```

---

### STEP 4: Polish & Ship (Phase 4)

```
PROMPT — PHASE 4 POLISH:

Everything works. Now make it portfolio-ready:

1. README.md — First impression for hiring managers:
   - Architecture diagram (Mermaid)
   - Live demo link
   - Tech stack badges
   - Quickstart guide
   - Key design decisions
   - Skills demonstrated
   - Cost: $0/month
   - Author: Kriti Srivastava

2. Complete remaining docs/ files
3. CI: .github/workflows/ci.yml (ruff + pytest + eslint + vite build)
4. Code quality: docstrings, type hints, no TODOs, no commented code
5. Lighthouse performance >90
6. CHANGELOG.md: v1.0.0
```

---

*End of PRD v3.0 — WellNow Staffing Optimization Focus*
*Tailored for TAG — The Aspen Group*
*Candidate: Kriti Srivastava*
