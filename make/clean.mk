.PHONY: clean
clean: ##@cleaning Remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test clean-others

.PHONY: clean-build
clean-build: ##@cleaning Clean Remove build artifacts
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ##@cleaning Clean Remove Python file artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

.PHONY: clean-test
clean-test: ##@cleaning Clean Remove test and coverage artifacts
clean-test:
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/

clean-others:
	rm -rf .vscode/.ropeproject/
