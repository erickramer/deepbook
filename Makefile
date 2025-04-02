# Ensure correct Python executable is used
VENV = test_venv
PYTHON = $(VENV)/bin/python
PYTEST = $(VENV)/bin/pytest

# Check if uv is available, otherwise use pip
ifeq ($(shell which uv),)
  $(info uv not found, using pip)
  INSTALLER = $(VENV)/bin/pip install -r
else
  $(info using uv for faster package installation)
  INSTALLER = uv pip install --python $(VENV)/bin/python -r
endif

run: venv install-dev
	$(VENV)/bin/streamlit run deepbook.py

install-dev: venv
	$(VENV)/bin/pip install -e .

venv:
	python -m venv $(VENV)
	$(INSTALLER) requirements.txt
	$(INSTALLER) requirements-dev.txt

hooks: venv
	mkdir -p .pre-commit-cache
	cp scripts/pre-commit.sh .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "Pre-commit hooks installed successfully."

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
