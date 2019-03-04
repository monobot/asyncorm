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
help: ## shows the help menu
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean-build
clean-build: ## remove build artifacts
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

.PHONY: clean
clean: ## remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test

.PHONY: lint
lint: ## check style with black code style
lint: clean
	black --check --diff .

test: ## run tests quickly with the default Python
	python -m tests

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
coverage: coverage run --source asyncorm setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

.PHONY: docs
docs: ## generate Sphinx HTML documentation, including API docs
docs: clean
	rm -f docs/asyncorm.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ asyncorm
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

servedocs: ## compile the docs watching for changes
servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: ## package and upload a release
release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: ## builds source and wheel package
dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: ## install the package to the active Python's site-packages
install: clean
	python setup.py install
