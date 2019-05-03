PHONY: docs
docs: ##@documentation Generate Sphinx HTML documentation, including API docs
docs: clean
	rm -f docs/asyncorm*.rst
	rm -f docs/modules.rst
	pipenv run sphinx-apidoc -o docs/ asyncorm
	pipenv run $(MAKE) -C docs clean
	pipenv run $(MAKE) -C docs html

PHONY: servedocs
servedocs: ##@documentation Compile the docs watching for changes
servedocs: docs
	pipenv run watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .
