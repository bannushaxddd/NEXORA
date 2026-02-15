.PHONY: install test run clean docker-up docker-down lint format

install:
	pip install -r requirements.txt

test:
	pytest --cov=src --cov-report=html --cov-report=term

test-watch:
	ptw -- --cov=src

run:
	uvicorn src.api.routes:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uvicorn src.api.routes:app --host 0.0.0.0 --port 8000 --workers 4

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f search-api

lint:
	flake8 src tests
	mypy src

format:
	black src tests
	isort src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

benchmark:
	python scripts/benchmark.py

# Run everything before commit
pre-commit: format lint test
	@echo "✅ All checks passed!"