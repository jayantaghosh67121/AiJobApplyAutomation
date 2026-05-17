.PHONY: help install install-dev dev test test-cov lint format migrate migrate-new clean docker-up docker-down docker-build

help:
	@echo "Job Automation Bot - Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start FastAPI dev server with auto-reload"
	@echo "  make worker           Start Celery worker"
	@echo "  make beat             Start Celery Beat scheduler"
	@echo "  make dashboard        Start Streamlit dashboard"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run ruff linter"
	@echo "  make format           Format code with black"
	@echo "  make type-check       Run mypy type checker"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run tests"
	@echo "  make test-cov         Run tests with coverage report"
	@echo "  make test-unit        Run only unit tests"
	@echo "  make test-integration Run only integration tests"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          Run Alembic migrations"
	@echo "  make migrate-new      Create new migration (usage: make migrate-new MSG=\"description\")"
	@echo "  make migrate-downgrade Downgrade one migration"
	@echo "  make db-init          Initialize database and run migrations"
	@echo "  make seed             Seed database with sample data"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start all services with docker-compose"
	@echo "  make docker-down      Stop all services"
	@echo "  make docker-logs      View docker-compose logs"
	@echo "  make docker-clean     Remove containers, volumes, and images"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Remove Python cache files and build artifacts"
	@echo "  make pre-commit       Run pre-commit hooks"
	@echo "  make requirements     Generate requirements.txt from pyproject.toml"

# Installation
install:
	uv sync --no-dev

install-dev:
	uv sync

# Development servers
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	celery -A app.worker.celery worker --loglevel=info

beat:
	celery -A app.worker.celery beat --loglevel=info

dashboard:
	streamlit run dashboard/app.py

# Code quality
lint:
	ruff check app/ tests/ --fix

format:
	black app/ tests/ --line-length 100

type-check:
	mypy app/

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

test-unit:
	pytest tests/ -v -m unit

test-integration:
	pytest tests/ -v -m integration

# Database operations
migrate:
	alembic upgrade head

migrate-new:
	alembic revision --autogenerate -m "$(MSG)"

migrate-downgrade:
	alembic downgrade -1

db-init: migrate seed

seed:
	python scripts/seed.py

# Pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Docker operations
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf build/ dist/

# Requirements generation (if using pip)
requirements:
	uv pip compile pyproject.toml -o requirements.txt
	uv pip compile pyproject.toml --all-extras -o requirements-dev.txt
