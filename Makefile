# Ensure correct Python executable is used
VENV = test_venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest

run:
	streamlit run app/__init__.py

venv:
	python -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

test: venv
	$(PYTEST)

coverage: venv
	$(PYTEST) --cov=app --cov-report=term-missing

lint: venv
	$(VENV)/bin/flake8 app tests
	$(VENV)/bin/black --check app tests
	$(VENV)/bin/isort --check-only --profile black app tests

format: venv
	$(VENV)/bin/black app tests
	$(VENV)/bin/isort app tests

clean:
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage

.PHONY: run venv test coverage lint format clean