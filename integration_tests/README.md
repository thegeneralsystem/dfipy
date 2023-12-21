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

```bash
pytest
```

## Datasets API

```bash
pytest test_datasets.py
```

## User API

```bash
pytest test_users_identities.py
```
