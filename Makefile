.PHONY: install run dashboard test lint format clean docker-build docker-up docker-pipeline help

# Default target
help:
	@echo "NewsLens — available commands:"
	@echo ""
	@echo "  Setup"
	@echo "    make install         Install all dependencies + spaCy model"
	@echo "    make setup-env       Copy .env.template to .env"
	@echo ""
	@echo "  Running"
	@echo "    make run             Run the full pipeline (ingest → analyze → store)"
	@echo "    make dashboard       Launch the Streamlit dashboard"
	@echo "    make ingest          Run data ingestion only"
	@echo ""
	@echo "  Testing & Linting"
	@echo "    make test            Run the test suite"
	@echo "    make test-cov        Run tests with coverage report"
	@echo "    make lint            Run flake8 linter"
	@echo "    make format          Format code with black"
	@echo ""
	@echo "  Docker"
	@echo "    make docker-build    Build Docker image"
	@echo "    make docker-up       Start Streamlit dashboard in Docker"
	@echo "    make docker-pipeline Run the full pipeline in Docker"
	@echo ""
	@echo "  Cleanup"
	@echo "    make clean           Remove __pycache__ and .pyc files"

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm
	python -m nltk.downloader punkt stopwords wordnet averaged_perceptron_tagger omw-1.4

setup-env:
	@if [ ! -f .env ]; then cp .env.template .env && echo "Created .env from template"; else echo ".env already exists"; fi

run:
	python run.py --full

dashboard:
	streamlit run app/dashboard.py

ingest:
	python run.py --ingest

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

lint:
	flake8 src/ app/ utils/ run.py --max-line-length=120 --exclude=__pycache__

format:
	black src/ app/ utils/ run.py tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true

docker-build:
	docker-compose build

docker-up:
	docker-compose up dashboard

docker-pipeline:
	docker-compose run --rm pipeline
