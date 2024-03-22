SOURCE_CODE = ./dfi
SOURCE_DOCS = ./docs
SOURCE_TESTS = ./tests
SOURCE_INTEGRATION_TESTS = ./integration_tests

# If An environment variable of PYTHON_VERSION is set then use that. otherwise uses the default set below
PYTHON_VERSION ?= "3.11"


.PHONY: dev develop-docker lock \
	ruff mypy \
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

lint:
	poetry run ruff check $(SOURCE_CODE) --fix
	poetry run ruff check $(SOURCE_DOCS) --fix
	poetry run ruff check $(SOURCE_TESTS) --fix
	poetry run ruff check $(SOURCE_INTEGRATION_TESTS) --fix

reformat:
	poetry run ruff format $(SOURCE_CODE)
	poetry run ruff format $(SOURCE_DOCS)
	poetry run ruff format $(SOURCE_TESTS)
	poetry run ruff format $(SOURCE_INTEGRATION_TESTS)

mypy: 
	poetry run mypy $(SOURCE_CODE)
	poetry run mypy $(SOURCE_TESTS)
	poetry run mypy $(SOURCE_INTEGRATION_TESTS)

static-analysis: reformat lint mypy

test:
	poetry run coverage run -m pytest --verbose tests --junitxml=junit.xml
	poetry run coverage xml

integration-tests:
	poetry run coverage run -m pytest --verbose integration_tests --junitxml=junit.xml
	poetry run coverage xml