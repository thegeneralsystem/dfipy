# Integrations Tests

Integration tests don't test for correctness of the API, only that `dfipy` can correctly make requests to the APIs.

Tests are run sequentially and in a specific order.

## Setup

Integration tests should be run in the `dev-env` using the profile `dfi-api-full`.

### Environment Variables

The `dev-env` sets up some environment variables that are automatically copied and sourced with the following command when running `make develop-docker`:

```bash
cp ../dev-environment/generated-config/dfi-api/dfi-api.env dfi-api.env
```

This assumes the `dev-environment` repo is in the same directory as this repo (e.g. `../`).

The following environment variables should then be set:

```bash
API_TOKEN=gs<...>
USERNAME=dev
DATASET=gs.dfi
DFI_INSTANCE=gs.dfi
```

## All Integration Tests

Since the integration tests are state-dependent and depend upon the state set in previous tests, we need to ensure tests are run in order. Each test within a module is numbered by the run order. We use `--order-scope=module` to run all tests within each module before running other modules. This ensures that each test module can run with a clean slate. To have a clean slate for each test module, all test modules should ensure that the "environment" is suitably clean upon setup and teardown. For example, checking that there is no data in the DFI before importing records and also truncating and deleting the dataset in the teardown.

```bash
pytest integration_tests/ --order-scope=module --log-cli-level=warning
```

## Import API

The integration tests for the Import API are setup to run off the users AWS SSO credentials until at which time the dev-env is setup with it's own AWS credentials. The aws profile used should have access to the following AWS S3 bucket to run tests: `s3://dev-ta-platform-dev-datasets/`.

To give the docker container running the integration tests access to the users AWS credentials, the credentials are mounted to the container when running `make dev $(AWS_PATH)`. This is hard-coded, because the docker command requires a global path:

```makefile
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
```

Then login to SSO and set the `AWS_PROFILE` environment variable.

```bash
aws sso login --profile <profile>
export AWS_PROFILE=<profile>
```
