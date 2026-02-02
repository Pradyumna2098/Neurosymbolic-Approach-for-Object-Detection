# Makefile for Neurosymbolic Object Detection

.PHONY: help install install-dev test test-backend test-pipeline test-frontend lint lint-python lint-frontend format clean docker-build docker-up docker-down docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install          - Install all dependencies"
	@echo "  install-dev      - Install development dependencies"
	@echo "  test             - Run all tests"
	@echo "  test-backend     - Run backend tests"
	@echo "  test-pipeline    - Run pipeline tests"
	@echo "  test-frontend    - Run frontend tests"
	@echo "  lint             - Run all linters"
	@echo "  lint-python      - Lint Python code"
	@echo "  lint-frontend    - Lint frontend code"
	@echo "  format           - Format all code"
	@echo "  docker-build     - Build Docker images"
	@echo "  docker-up        - Start all services with Docker Compose"
	@echo "  docker-down      - Stop all services"
	@echo "  clean            - Remove build artifacts and caches"

# Installation
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r backend/requirements.txt
	cd frontend && npm install

install-dev: install
	pip install pytest pytest-cov flake8 black httpx

# Testing
test: test-backend test-pipeline

test-backend:
	pytest tests/backend/ -v --cov=backend --cov-report=term

test-pipeline:
	pytest tests/pipeline/ -v --cov=pipeline --cov-report=term

test-frontend:
	cd frontend && npm test -- --coverage --watchAll=false

# Linting
lint: lint-python lint-frontend

lint-python:
	flake8 backend/ pipeline/ --max-line-length=88 --extend-ignore=E203,W503
	black --check backend/ pipeline/

lint-frontend:
	cd frontend && npx prettier --check "src/**/*.{js,jsx,css}"

# Formatting
format:
	black backend/ pipeline/
	cd frontend && npx prettier --write "src/**/*.{js,jsx,css}"

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Cleaning
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf frontend/node_modules
	rm -rf frontend/build

# Running services
run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm start

# Database/Monitoring
monitoring-up:
	docker-compose up -d prometheus grafana

monitoring-down:
	docker-compose stop prometheus grafana
