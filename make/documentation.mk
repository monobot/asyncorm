PHONY: docs
docs: ##@documentation Generate Sphinx HTML documentation, including API docs
docs: clean
	rm -f docs/asyncorm*.rst
	rm -f docs/modules.rst
	PIPENV_DONT_LOAD_ENV=1 pipenv run sphinx-apidoc -o docs/ asyncorm
	PIPENV_DONT_LOAD_ENV=1 pipenv run $(MAKE) -C docs clean
	PIPENV_DONT_LOAD_ENV=1 pipenv run $(MAKE) -C docs html

PHONY: servedocs
servedocs: ##@documentation Compile the docs watching for changes
servedocs: docs
	PIPENV_DONT_LOAD_ENV=1 pipenv run watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .
