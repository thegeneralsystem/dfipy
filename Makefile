SOURCE_CODE = ./dfi
SOURCE_DOCS = ./docs
SOURCE_TESTS = ./tests
SOURCE_INTEGRATION_TESTS = ./integration_tests
PACKAGE_VERSION := $(shell mkversion pep440)
# If An environment variable of PYTHON_VERSION is set then use that. otherwise uses the default set below
PYTHON_VERSION ?= "3.11"


.PHONY: dev develop-docker lock \
	black isort flake8 pylint mypy \
	reformat static-analysis lint \
	test integration-tests

dev: 
	cp ../dev-environment/generated-config/dfi-api/dfi-api.env dfi-api.env

	docker build -t dfipy .

	docker run --rm -it \
	--network exc_dev \
	--env-file dfi-api.env \
	--env-file tests.env \
	--workdir /home/dev \
	--volume .:/home/dev \
	--volume $(AWS_PATH)/.aws:/home/dev/.aws \
	--entrypoint /bin/bash \
	dfipy

lock:
	poetry update
	poetry install
	poetry lock

black:
	poetry run black $(SOURCE_CODE)
	poetry run black $(SOURCE_DOCS)
	poetry run black $(SOURCE_TESTS)
	poetry run black $(SOURCE_INTEGRATION_TESTS)

isort:
	poetry run isort $(SOURCE_CODE)
	poetry run isort $(SOURCE_DOCS)
	poetry run isort $(SOURCE_TESTS) 
	poetry run isort $(SOURCE_INTEGRATION_TESTS)

flake8:
	poetry run flake8 $(SOURCE_CODE)
	poetry run flake8 $(SOURCE_TESTS)
	poetry run flake8 $(SOURCE_INTEGRATION_TESTS)

pylint: 
	poetry run pylint $(SOURCE_CODE)
	poetry run pylint  --exit-zero $(SOURCE_TESTS)
	poetry run pylint  --exit-zero $(SOURCE_INTEGRATION_TESTS)

mypy: 
	poetry run mypy $(SOURCE_CODE)
	poetry run mypy $(SOURCE_TESTS)
	poetry run mypy $(SOURCE_INTEGRATION_TESTS)

reformat: black isort
static-analysis: flake8 pylint
lint: reformat static-analysis

test:
	poetry run coverage run -m pytest --verbose tests --junitxml=junit.xml
	poetry run coverage xml

integration-tests:
	poetry run coverage run -m pytest --verbose integration_tests --junitxml=junit.xml
	poetry run coverage xml