# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Phase 4: Polish (README live links, Vercel deploy, complete remaining docs, Lighthouse >90)

## [0.5.0] - 2026-02-23

### Added — Phase 3: React Dashboard
- Vite + React 18 + Tailwind CSS + Recharts + React Router v6 scaffold
- **Page 1 — Hero/Landing**: Candidate intro, pipeline flow diagram, tech stack grid, key stats
- **Page 2 — Architecture Deep Dive**: Interactive pipeline diagram, component cards, GCP cost breakdown
- **Page 3 — Staffing Dashboard (PRIMARY)**: 6 KPI cards, coverage scatter chart, gap heatmap, labor cost trend line, overtime waterfall bar chart, float deployment planner table
- **Page 4 — Data Quality Monitor**: Freshness indicator, DQ scorecard by severity with weighted scoring, pipeline runs history table
- **Page 5 — SQL Showcase**: 3 featured BigQuery queries with syntax highlighting, sample results, and business explanations
- **Page 6 — How I Built This**: Development timeline, AI-assisted process, challenges & solutions
- Interactive filters: region and location type toggle buttons with real-time chart updates
- Custom `useDataLoader` hook with in-memory caching for pre-computed JSON files
- Code splitting: React, Recharts, and app code in separate chunks (67KB + 162KB + 396KB)
- Vercel deployment config (`vercel.json`) with SPA rewrites
- Data files copied from ETL pipeline export to `public/data/` (7 JSON files)

## [0.4.0] - 2026-02-23

### Added — Phase 2.5: GCP Deployment (Real Infrastructure)
- HRIS API deployed to Cloud Run (`https://wellnow-hris-api-3vhsvfwxyq-uc.a.run.app`)
- ETL pipeline deployed to Cloud Functions 2nd Gen (1024MB, 540s timeout)
- Cloud Scheduler configured for daily 6AM UTC pipeline trigger
- BigQuery dataset `people_analytics` live with 9 tables (4 dim, 2 fact, 3 utility)
- Cloud Storage buckets for raw JSON staging and dashboard data export
- Secret Manager storing HRIS API key
- First successful end-to-end pipeline run: 177,182 records extracted, 176,972 loaded

### Fixed
- Dockerfile PORT mismatch: Cloud Run injects PORT=8080, CMD now uses `$PORT` dynamically
- `.env` sourcing: replaced `export $(grep | xargs)` with `set -a; source; set +a` across all 7 scripts
- Cron value quoting: `SCHEDULER_CRON="0 6 * * *"` to prevent shell word splitting
- BigQuery type casting: `started_at`/`completed_at` → `pd.to_datetime()`, `check_date` → `.dt.date` for pyarrow compatibility
- Cloud Function memory: bumped from 512MB to 1024MB to accommodate 177K-record transform stage
- Cloud Function entry point: staging directory deploy pattern preserving `src.etl.*` absolute imports

## [0.3.0] - 2026-02-22

### Added — Phase 2: ETL Pipeline
- ETL pipeline orchestrator (`pipeline.py`) with run_id tracking and stage metrics
- Extract module with paginated API calls and exponential backoff retry logic
- Validate module implementing all 15 DQ rules from `quality_rules.yaml`
- Transform module: dim_employee (SCD Type 2), dim_location, dim_job, fact_daily_staffing, fact_shift_gap
- Load module: BigQuery load jobs (TRUNCATE dims, APPEND facts) with LOCAL_MODE support
- Dashboard data export: 7 pre-computed JSON files (KPIs, coverage, gaps, overtime, costs, DQ, pipeline runs)
- Config settings with YAML loader and `${VAR}` env-var interpolation
- Pydantic validation schemas for all 5 data entities
- Utility modules: structured JSON logger, retry decorator, pipeline metrics, GCP helpers
- Cloud Function HTTP entry point (`main.py`)
- Full test suite: 38 unit tests passing (extract, validate, transform, load)
- Integration test: end-to-end pipeline against live local API (177,182 records, 10.2s)

## [0.2.0] - 2026-02-22

### Added — Phase 1: Simulated HRIS API
- FastAPI application with 7 REST endpoints for workforce data
- Faker-based deterministic data generation (MASTER_SEED=42)
- 1,200 employees across 80 locations in 15 states, 18 months of history
- API key authentication middleware
- Pydantic v2 strict-mode response models
- Multi-stage Dockerfile with non-root user and HEALTHCHECK
- Full test suite: 52 tests passing (generators, auth, all endpoints)

## [0.1.0] - 2026-02-22

### Added — Step 0: Architecture & Documentation
- Initial repository structure following enterprise conventions
- BigQuery schema definitions (4 dimensions, 2 facts, 3 utility tables)
- Architecture documentation with Mermaid diagrams
- Data dictionary covering all tables and fields
- Data lineage documentation
- Security and compliance documentation
- API specification for simulated HRIS endpoints
- Data quality rules (15 rules) externalized to YAML
- Makefile with setup, test, lint, and deploy targets
- CI/CD workflow templates for GitHub Actions
- Infrastructure deployment scripts for GCP
