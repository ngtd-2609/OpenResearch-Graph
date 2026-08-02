SHELL := /bin/sh
PYTHONPATH := backend:.

.PHONY: setup up down logs doctor migrate migration seed test test-db lint format backup restore ingest-sample train-baseline evaluate clean

setup:
	docker compose up -d postgres redis
	docker compose run --rm backend alembic upgrade head
	docker compose run --rm backend python -m app.scripts.seed

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200 backend worker frontend

doctor:
	python scripts/system_doctor.py

migrate:
	docker compose run --rm backend alembic upgrade head

migration:
	@test -n "$(MESSAGE)" || (echo "Usage: make migration MESSAGE='describe change'" && exit 1)
	docker compose run --rm backend alembic revision --autogenerate -m "$(MESSAGE)"

seed:
	docker compose run --rm backend python -m app.scripts.seed

test:
	cd backend && PYTHONPATH=.:.. pytest tests --ignore=tests/integration --cov=app --cov-fail-under=80
	cd frontend && npm run test:run

test-db:
	cd backend && RUN_DB_TESTS=1 PYTHONPATH=.:.. pytest tests/integration -q

lint:
	cd backend && python -m ruff check app tests alembic ../data_pipeline
	cd frontend && npm run lint && npm run typecheck

format:
	cd backend && python -m ruff format app tests alembic ../data_pipeline
	cd frontend && npm run format

backup:
	powershell -ExecutionPolicy Bypass -File scripts/windows/backup_database.ps1

restore:
	@test -n "$(FILE)" || (echo "Usage: make restore FILE=backups/file.sql" && exit 1)
	powershell -ExecutionPolicy Bypass -File scripts/windows/restore_database.ps1 -BackupFile "$(FILE)"

ingest-sample:
	docker compose run --rm backend python -m data_pipeline.ingestion.openalex --query "machine learning" --max-records 100

train-baseline:
	docker compose run --rm backend python -m app.ml.training.train_relevance --config configs/relevance.yaml

evaluate:
	@echo "Run notebooks/02_search_baseline.ipynb, 03_recommendation_baseline.ipynb and 04_model_evaluation.ipynb"

clean:
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache \) -prune -exec rm -rf {} +
