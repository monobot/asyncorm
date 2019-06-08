setup: ##@deploy Installs pipenv enviroment
setup:
	pip install pipenv
	PIPENV_DONT_LOAD_ENV=1 pipenv install --dev

release: ##@deploy Package and upload a release
release: dist
	PIPENV_DONT_LOAD_ENV=1 pipenv run twine upload dist/*

dist: ##@deploy Builds source and wheel package
dist: clean
	PIPENV_DONT_LOAD_ENV=1 pipenv run python setup.py sdist
	PIPENV_DONT_LOAD_ENV=1 pipenv run python setup.py bdist_wheel
	ls -l dist

install: ##@deploy Install the package to the active Python's site-packages
install: clean
	PIPENV_DONT_LOAD_ENV=1 pipenv run python setup.py install
