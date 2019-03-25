setup: ##@deploy Installs pipenv enviroment
setup:
	pip install pipenv
	pipenv install --dev

release: ##@deploy Package and upload a release
release: dist
	pipenv run twine upload dist/*

dist: ##@deploy Builds source and wheel package
dist: clean
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel
	ls -l dist

install: ##@deploy Install the package to the active Python's site-packages
install: clean
	pipenv run python setup.py install
