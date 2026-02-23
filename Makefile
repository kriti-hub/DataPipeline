# =============================================================================
# WellNow Staffing Analytics — Makefile
# =============================================================================

.PHONY: setup test lint deploy-api deploy-etl deploy-dashboard clean help

# --- Setup ---
setup: setup-api setup-etl setup-dashboard  ## Install all dependencies

setup-api:
	cd src/api && pip install -r requirements.txt -r requirements-dev.txt

setup-etl:
	cd src/etl && pip install -r requirements.txt -r requirements-dev.txt

setup-dashboard:
	cd src/dashboard && npm install

# --- Test ---
test: test-api test-etl  ## Run all tests

test-api:
	cd src/api && python -m pytest tests/ -v --tb=short

test-etl:
	cd src/etl && python -m pytest tests/ -v --tb=short

# --- Lint ---
lint: lint-api lint-etl lint-dashboard  ## Run all linters

lint-api:
	cd src/api && ruff check . && ruff format --check .

lint-etl:
	cd src/etl && ruff check . && ruff format --check .

lint-dashboard:
	cd src/dashboard && npx eslint src/

# --- Deploy ---
deploy-api:  ## Deploy HRIS API to Cloud Run
	bash infrastructure/scripts/deploy_api.sh

deploy-etl:  ## Deploy ETL pipeline to Cloud Functions
	bash infrastructure/scripts/deploy_etl.sh

deploy-dashboard:  ## Deploy dashboard to Vercel
	cd src/dashboard && npx vercel --prod

# --- Local Development ---
run-api:  ## Run API locally
	cd src/api && uvicorn main:app --reload --port 8000

run-dashboard:  ## Run dashboard locally
	cd src/dashboard && npm run dev

run-etl:  ## Run ETL pipeline locally
	cd src/etl && python -m pipeline

# --- Database ---
setup-bigquery:  ## Create BigQuery schema
	bash infrastructure/scripts/setup_bigquery.sh

# --- Clean ---
clean:  ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true

# --- Help ---
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
