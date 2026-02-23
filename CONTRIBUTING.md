# Contributing to WellNow Staffing Analytics

Thank you for your interest in contributing to this project.

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your values
3. Run `make setup` to install all dependencies
4. Run `make test` to verify everything works

## Code Standards

- **Python:** Follow PEP 8. Use type hints on all function parameters and return values. Run `ruff` for linting.
- **JavaScript/React:** Follow ESLint configuration. Use functional components with hooks.
- **SQL:** Use uppercase keywords, lowercase identifiers, and descriptive aliases.

## Branch Naming

- `feature/<description>` for new features
- `fix/<description>` for bug fixes
- `docs/<description>` for documentation changes

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear, atomic commits
3. Ensure all tests pass (`make test`)
4. Ensure linting passes (`make lint`)
5. Submit a PR using the provided template
6. Request review from a code owner

## Project Structure

- `src/api/` — Simulated HRIS REST API (FastAPI)
- `src/etl/` — ETL pipeline (Python, BigQuery)
- `src/dashboard/` — React dashboard (Vite, Tailwind, Recharts)
- `sql/` — BigQuery schema and queries
- `docs/` — Architecture and operational documentation
- `config/` — Shared configuration files

Each `src/` module is independently deployable and has its own `tests/` directory.
