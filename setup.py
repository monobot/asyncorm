from setuptools import setup

from asyncorm import __version__

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()


def requirement_parser(file_name):
    try:
        with open(file_name, "r") as req_file:
            file_requirement = []
            for line in req_file.readlines():
                line = line.rstrip("\n")
                if line.startswith("-r"):
                    file_requirement += requirement_parser(line.split(" ")[1])
                elif line:
                    file_requirement += [line]
    except FileNotFoundError:
        file_requirement = ""
    return file_requirement


requirements = requirement_parser("requirements.txt")
test_requirements = requirement_parser("requirements_dev.txt")

setup(
    name="asyncorm",
    version=__version__,
    description="A fully asynchronous python ORM",
    long_description=readme + "\n\n" + history,
    author="Héctor Alvarez (monobot)",
    author_email="monobot.soft@gmail.com",
    url="https://github.com/monobot/asyncorm",
    packages=["asyncorm"],
    package_dir={"asyncorm": "asyncorm"},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="asyncorm",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    test_suite="tests",
    tests_require=test_requirements,
    entry_points={"console_scripts": ["orm_setup=asyncorm.application.commands.orm_setup:setup"]},
)
