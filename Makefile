.PHONY: help up down ingest dbt-run dbt-test test clean

help:
	@echo "IMDb Movie Analysis DWH Pipeline Commands:"
	@echo "  make up          - Start PostgreSQL and Airflow via Docker Compose"
	@echo "  make down        - Stop and remove Docker containers"
	@echo "  make ingest      - Download sample IMDb datasets and load into raw PostgreSQL schema"
	@echo "  make dbt-run     - Run dbt staging, intermediate, and mart models"
	@echo "  make dbt-test    - Execute dbt generic and custom data quality tests"
	@echo "  make test        - Run Python unit tests with pytest"
	@echo "  make clean       - Remove temporary logs, target folders, and cache"

up:
	docker-compose up -d --build

down:
	docker-compose down -v

ingest:
	python src/ingest_imdb.py --sample

dbt-run:
	dbt run --profiles-dir dbt_imdb --project-dir dbt_imdb

dbt-test:
	dbt test --profiles-dir dbt_imdb --project-dir dbt_imdb

test:
	pytest tests/ -v

clean:
	rm -rf dbt_imdb/target dbt_imdb/logs .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
