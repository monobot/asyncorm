.DEFAULT_GOAL := help

.PHONY: help
help: ## Show the help menu
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean-build
clean-build: ## Clean Remove build artifacts
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## Clean Remove Python file artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

.PHONY: clean-test
clean-test: ## Clean Remove test and coverage artifacts
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

PHONY: coverage
coverage: ## Check code coverage quickly with the default Python
coverage:
	pipenv run coverage run -m tests
	pipenv run coverage report -m
	pipenv run coverage html
	xdg-open htmlcov/index.html

PHONY: report-coverage
report-coverage: ## Report coverage results to codacy
report-coverage:
	pipenv run python-codacy-coverage -r coverage.xml

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
