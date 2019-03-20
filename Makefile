.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help: ## Show the help menu
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean-build
clean-build: ## Remove build artifacts
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## Remove Python file artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

.PHONY: clean-test
clean-test: ## Remove test and coverage artifacts
clean-test:
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/

clean-others:
	rm -rf .vscode/.ropeproject/

.PHONY: clean
clean: ## Remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test clean-others

.PHONY: isort
isort: ## Check imports sorting
isort: clean-others
	pipenv run isort --diff

.PHONY: lint
lint: ## Check style with black code style
lint: clean-others
	pipenv run black --check --diff -l 119 .

setup:
	pip install pipenv
	pipenv install --dev

test: ## Run tests quickly with the default Python
	pipenv run python -m tests

test-all: ## Run tests on every Python version with tox
	pipenv run tox

coverage: ## Check code coverage quickly with the default Python
coverage: coverage run --source asyncorm setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

.PHONY: docs
docs: ## Generate Sphinx HTML documentation, including API docs
docs: clean
	rm -f docs/asyncorm.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ asyncorm
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

servedocs: ## Compile the docs watching for changes
servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: ## Package and upload a release
release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: ## Builds source and wheel package
dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: ## Install the package to the active Python's site-packages
install: clean
	python setup.py install
