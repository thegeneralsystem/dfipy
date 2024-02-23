"""Pytest configuration file."""

import json
import logging
import os
import time
from dataclasses import dataclass

import pytest

from dfi import Client
from dfi.services.ingest import BatchURLFiles, CSVFormat, S3URLPresigner

TOKEN = os.environ["API_TOKEN"]
DATASET_ID = os.environ["DATASET"]
IMPORT_URL = os.environ["DFI_IMPORT_API_URL"]
QUERY_URL = os.environ["DFI_QUERY_API_URL"]
DATASETS_API_URL = os.environ["DFI_DATASETS_API_URL"]
USERS_IDENTITIES_API_URL = os.environ["DFI_USERS_API_URL"]

TEST_DATASET_S3_BUCKET = "dev-ta-platform-dev-datasets"
TEST_DATASET_S3_PREFIX = "test/integration-tests/100k_with_filter_fields_epoc_2023-11-08"
TEST_DATASET_S3_REGION = "eu-west-2"
DATASET_DEFINITION = "integration_tests/datasets/test-dataset.json"
AWS_PROFILE = os.environ["AWS_PROFILE"]  # TODO change this once dev-ops have enabled AWS SSO access

NUM_RECORDS = 99_999

_logger = logging.getLogger(__name__)


@dataclass
class ValueStore:
    """Used to store and reuse values across tests."""

    dataset_id: str
    import_batch_id: str


@pytest.fixture(name="dataset_name", scope="module")
def get_dataset_name() -> str:
    with open("integration_tests/datasets/test-dataset.json", encoding="utf-8") as fp:
        dataset = json.load(fp)
    name: str = dataset["name"]
    return name


@pytest.fixture(name="s3_presigner", scope="module")
def get_s3_presigner() -> S3URLPresigner:
    return S3URLPresigner(TEST_DATASET_S3_BUCKET, TEST_DATASET_S3_REGION, AWS_PROFILE)


@pytest.fixture(name="import_batch_id", scope="module")
def get_import_batch_id(value_store: ValueStore) -> str:
    return value_store.import_batch_id


@pytest.fixture(name="dataset_id", scope="module")
def get_dataset_id(value_store: ValueStore) -> str:
    return value_store.dataset_id


@pytest.fixture(name="dataset_schema", scope="module")
def get_dataset_schema(dataset_id: str) -> str:
    dfi_datasets = Client(TOKEN, DATASETS_API_URL)
    return dfi_datasets.datasets.get_schema(dataset_id)


@pytest.fixture(name="dfi", scope="module")
def get_dfi_client() -> Client:
    return Client(TOKEN, QUERY_URL)


def import_test_data(dfi: Client, dataset_id: str, s3_presigner: S3URLPresigner, value_store: ValueStore) -> None:
    prefix = TEST_DATASET_S3_PREFIX
    signed_urls = s3_presigner.generate_presigned_urls(prefix, ".csv", expiration=5)
    source = BatchURLFiles(signed_urls)

    csv_format = CSVFormat(
        entity_id=0,
        timestamp=1,
        longitude=2,
        latitude=3,
        ipv4=4,
        age=5,
        home_ipv4=6,
        route_id=7,
        credit_card_provider=8,
        transportation_mode=9,
    )

    report = dfi.ingest.put_batch(dataset_id=dataset_id, source=source, file_format=csv_format, dry_run=False)

    assert isinstance(report, dict)
    assert report["status"] == "created"

    # store the import batch id for following tests
    value_store.import_batch_id = report["id"]

    # Poll until import finished (~4 seconds)
    status = dfi.ingest.get_batch_status(value_store.import_batch_id)
    while status[0]["status"] not in ["finished", "error"]:
        time.sleep(1)
        status = dfi.ingest.get_batch_status(value_store.import_batch_id)

    assert isinstance(status, list)
    assert status[0]["invalidCount"] == 0
    assert status[0]["insertCount"] == NUM_RECORDS


@pytest.fixture(scope="module", autouse=True)
def setup_teardown(dataset_name: str, s3_presigner: S3URLPresigner, value_store: ValueStore) -> None:
    """Fixture to setup and teardown the dfi for the tests in this module.

    Setup:
        - truncate dfi
        - check dfi is empty
        - create dataset with schema
        - import data
        - check it's all working
    Teardown:
        - truncate dfi
        - check dfi is empty
        - delete dataset
    """
    # SETUP
    _logger.info("SETUP")
    dfi_query = Client(TOKEN, QUERY_URL)
    dfi_import = Client(TOKEN, IMPORT_URL)
    dfi_datasets = Client(TOKEN, DATASETS_API_URL)
    dfi_users_identities = Client(TOKEN, USERS_IDENTITIES_API_URL)

    # Truncate the DFI (default dataset on dev-env startup)
    _logger.info("Truncating data...")
    dfi_query.delete.truncate(DATASET_ID)
    count = dfi_query.query.record_counts(DATASET_ID)
    assert count == 0

    # Create dataset with schema pointing to the DFI
    # Give dev-env user write permissions
    with open(DATASET_DEFINITION, encoding="utf-8") as fp:
        dataset = json.load(fp)

    # Delete an existing dataset with the same name (useful if tests failed without proper teardown)
    _logger.info("Deleting dataset...")
    existing_dataset = dfi_datasets.datasets.find(name=dataset_name, limit=1)
    if len(existing_dataset) > 0:
        dfi_datasets.datasets.delete(existing_dataset[0]["id"])

    _logger.info("Creating dataset...")
    created_dataset = dfi_datasets.datasets.create(dataset)

    dataset_id = created_dataset["id"]
    value_store.dataset_id = dataset_id

    _logger.info("Setting permissions...")
    identity = dfi_users_identities.identities.get_my_identity()
    write_permission = {"type": "writer", "scope": "identity", "identityId": identity["id"]}

    _ = dfi_datasets.datasets.add_permissions(dataset_id=dataset_id, permissions=[write_permission])
    my_permissions = dfi_datasets.datasets.get_my_permissions(dataset_id=dataset_id)

    assert my_permissions["write"] is True

    # Import data
    _logger.info("Importing data...")
    import_test_data(dfi_import, dataset_id, s3_presigner, value_store)

    # TEST CODE
    yield

    # TEARDOWN
    _logger.info("TEARDOWN")

    # Truncate DFI
    dfi_query.delete.truncate(dataset_id)
    count = dfi_query.query.record_counts(dataset_id)
    assert count == 0

    # Delete Dataset
    dfi_datasets.datasets.delete(dataset_id)

    _logger.info("COMPLETE")
