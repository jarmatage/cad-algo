.PHONY: run clean

VENV := .venv
PYTHON := $(shell which python3.13)
PYTEST = $(VENV)/bin/pytest
PIP := $(VENV)/bin/pip3
MYPY := $(VENV)/bin/mypy
RUFF := $(VENV)/bin/ruff

run: $(VENV)/bin/activate
	$(RUFF) format
	$(MYPY) src
	$(RUFF) check
	$(PYTEST)

$(VENV)/bin/activate: pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -e .[dev]

clean:
	find src tests -type d -name "__pycache__" -exec rm -r {} +
