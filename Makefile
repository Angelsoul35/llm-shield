.PHONY: install test lint run demo clean

install:
	pip install -e ".[dev]"

test:
	pytest --cov=llm_shield --cov-report=term-missing

lint:
	ruff check llm_shield tests

run:
	uvicorn llm_shield.main:app --reload --port 8000

demo:
	python -m llm_shield.cli demo

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
