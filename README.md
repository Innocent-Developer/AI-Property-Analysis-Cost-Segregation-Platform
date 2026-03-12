## AI Property Analysis & Cost Segregation Platform - Backend

This is a production-ready FastAPI backend skeleton for an AI-driven Property Analysis & Cost Segregation platform.

### Tech stack

- **Python** 3.11
- **FastAPI**
- **SQLAlchemy** ORM
- **PostgreSQL** (primary database)
- **Alembic** (migrations)
- **Redis** (queue / cache)
- **Celery** (background workers)
- **Pydantic** (validation & settings)

### Quick start (development)

1. Create and configure environment:

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. Run the API:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Run Celery worker:

   ```bash
   celery -A app.workers.celery_app.celery worker -l info
   ```

4. Apply migrations (after configuring Alembic):

   ```bash
   alembic upgrade head
   ```

### Project structure

The `app/` directory contains the FastAPI application:

- `config/` – environment-driven settings
- `database/` – DB engine & session management
- `models/` – SQLAlchemy ORM models
- `schemas/` – Pydantic request/response models
- `services/` – business logic & orchestration
- `routes/` – API routers
- `ai/` – AI model integration & helpers
- `pipelines/` – analysis & ETL-style pipelines
- `rules_engine/` – rule evaluation & compliance logic
- `financial_engine/` – financial calculations & projections
- `report_generator/` – report assembly & export
- `workers/` – Celery workers & tasks
- `utils/` – shared helpers & utilities
- `storage/` – storage abstractions (e.g., S3, local)

