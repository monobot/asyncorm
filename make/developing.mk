.PHONY: lint
lint: ##@developing Check style with black code style
lint: clean-others
	PIPENV_DONT_LOAD_ENV=1 pipenv run black --check --diff -l 119 .

.PHONY: isort
isort: ##@developing Check imports sorting
isort: clean-others
	PIPENV_DONT_LOAD_ENV=1 pipenv run isort --diff

test: ##@developing Run tests quickly with the default Python
	PIPENV_DONT_LOAD_ENV=1 pipenv run python -m tests

test-all: ##@developing Run tests on every Python version with tox
	PIPENV_DONT_LOAD_ENV=1 pipenv run tox

PHONY: coverage
coverage: ##@developing Check code coverage quickly with the default Python
coverage:
	PIPENV_DONT_LOAD_ENV=1 pipenv run coverage run -m tests
	PIPENV_DONT_LOAD_ENV=1 pipenv run coverage report -m
	PIPENV_DONT_LOAD_ENV=1 pipenv run coverage html
	xdg-open htmlcov/index.html

PHONY: report-coverage
report-coverage: ##@developing Report coverage results to codacy
report-coverage:
	PIPENV_DONT_LOAD_ENV=1 pipenv run python-codacy-coverage -r coverage.xml
