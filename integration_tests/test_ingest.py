"""Integration tests for the Import module.

Since these tests have side effects on the Import API service and some rely on the state
of the service, the order in which the tests are run matters.  We use pytest-order to specify 
the order in qhich tests are run.

These tests don't test for correctness of the API, only for correctness of the python wrapper.
"""

# pylint: disable=too-many-locals
import json
import logging
import os
import time

import pytest
from integration_tests.conftest import ValueStore

from dfi import Client
from dfi.services.ingest import AWSCredentials, BatchS3Files, BatchURLFiles, CSVFormat, S3URLPresigner

TOKEN = os.environ["API_TOKEN"]
DATASET_ID = os.environ["DATASET"]
IMPORT_URL = os.environ["DFI_IMPORT_API_URL"]
QUERY_URL = os.environ["DFI_QUERY_API_URL"]
DATASETS_API_URL = os.environ["DFI_DATASETS_API_URL"]
USERS_IDENTITIES_API_URL = os.environ["DFI_USERS_API_URL"]

DATASET_NAME = "test-ingest"
TEST_DATASET_S3 = "s3://dev-ta-platform-dev-datasets/test/integration-tests/100k_with_filter_fields_epoc_2023-11-08/"
TEST_DATASET_S3_BUCKET = "dev-ta-platform-dev-datasets"
TEST_DATASET_S3_PREFIX = "test/integration-tests/100k_with_filter_fields_epoc_2023-11-08"
TEST_DATASET_S3_REGION = "eu-west-2"
AWS_PROFILE = os.environ["AWS_PROFILE"]  # TODO change this once dev-ops have enabled AWS SSO access
DATASET_FILE = "integration_tests/datasets/ingest-dataset.json"

_logger = logging.getLogger(__name__)


@pytest.fixture(name="dataset_name", scope="module")
def get_dataset_name() -> str:
    with open(DATASET_FILE, encoding="utf-8") as fp:
        dataset = json.load(fp)
    return dataset["name"]


@pytest.fixture(name="s3_presigner", scope="module")
def get_s3_presigner() -> str:
    return S3URLPresigner(TEST_DATASET_S3_BUCKET, TEST_DATASET_S3_REGION, AWS_PROFILE)


@pytest.fixture(name="import_batch_id", scope="module")
def get_import_batch_id(value_store: ValueStore) -> str:
    return value_store.import_batch_id


@pytest.fixture(name="dataset_id", scope="module")
def get_dataset_id(value_store: ValueStore) -> str:
    return value_store.dataset_id


@pytest.fixture(scope="module", autouse=True)
def setup_teardown(dataset_name: str, value_store: ValueStore):
    """Fixture to setup and teardown the dfi for the tests in this module.
    Setup:
        - truncate dfi
        - check dfi is empty
        - create dataset with schema
        - check it's all gucci
    Teardown:
        - truncate dfi
        - check dfi is empty
        - delete dataset
    """
    # SETUP
    _logger.info("SETUP")
    dfi_query = Client(TOKEN, QUERY_URL)
    dfi_datasets = Client(TOKEN, DATASETS_API_URL)
    dfi_users_identities = Client(TOKEN, USERS_IDENTITIES_API_URL)

    # Truncate the DFI (default dataset on dev-env startup)
    dfi_query.delete.truncate(DATASET_ID)
    count = dfi_query.get.records_count(DATASET_ID)
    assert count == 0

    # Create dataset with schema pointing to the DFI
    # Give dev-env user write permissions
    with open(DATASET_FILE, encoding="utf-8") as fp:
        dataset = json.load(fp)

    # Delete an existing dataset with the same name (useful if tests failed without proper teardown)
    existing_dataset = dfi_datasets.datasets.find(name=dataset_name, limit=1)
    if len(existing_dataset) > 0:
        dfi_datasets.datasets.delete(existing_dataset[0]["id"])

    created_dataset = dfi_datasets.datasets.create(dataset)
    dataset_id = created_dataset["id"]
    value_store.dataset_id = dataset_id

    identity = identity = dfi_users_identities.identities.get_my_identity()
    write_permission = {"type": "writer", "scope": "identity", "identityId": identity["id"]}

    _ = dfi_datasets.datasets.add_permissions(dataset_id=dataset_id, permissions=[write_permission])
    my_permissions = dfi_datasets.datasets.get_my_permissions(dataset_id=dataset_id)

    assert my_permissions["write"] is True

    # TEST CODE
    yield

    # TEARDOWN
    _logger.info("TEARDOWN")

    # Truncate DFI
    dfi_query.delete.truncate(dataset_id)
    count = dfi_query.get.records_count(dataset_id)
    assert count == 0

    # Delete Dataset
    dfi_datasets.datasets.delete(dataset_id)

    _logger.info("COMPLETE")


@pytest.mark.order(0)
def test_get_aws_trust_policy() -> None:
    dfi = Client(TOKEN, IMPORT_URL)
    policy = dfi.ingest.get_aws_trust_policy()

    assert isinstance(policy, dict)


@pytest.mark.order(1)
@pytest.mark.skip(reason="don't currently understand the workflow")
def test_batch_s3_files_dry_run(dataset_id: str) -> None:
    dfi = Client(TOKEN, IMPORT_URL)

    # AWS Credentials
    role_arn = "arn:aws:s3:::dev-ta-platform-dev-datasets/test/integration-tests/5M_with_filter_fields_epoc_2023-11-08/"
    credentials = AWSCredentials(role_arn)
    bucket = TEST_DATASET_S3_BUCKET
    prefix = TEST_DATASET_S3_PREFIX
    glob = "*.csv"

    source = BatchS3Files(bucket, credentials, glob, prefix)

    # required fields
    entity_id = 0
    timestamp = 1
    longitude = 2
    latitude = 3

    # extra fields
    ipv4 = 4
    age = 5
    home_ipv4 = 6
    route_id = 7
    credit_card_provider = 8
    transportation_mode = 9

    csv_format = CSVFormat(
        entity_id=entity_id,
        timestamp=timestamp,
        longitude=longitude,
        latitude=latitude,
        ipv4=ipv4,
        age=age,
        home_ipv4=home_ipv4,
        route_id=route_id,
        credit_card_provider=credit_card_provider,
        transportation_mode=transportation_mode,
    )

    report = dfi.ingest.put_batch(dataset_id=dataset_id, source=source, file_format=csv_format, dry_run=True)

    assert isinstance(report, dict)


@pytest.mark.order(2)
@pytest.mark.skip(reason="don't currently understand the workflow")
def test_batch_s3_files(dataset_id: str, value_store: ValueStore) -> None:
    dfi = Client(TOKEN, IMPORT_URL)

    # AWS Credentials
    role_arn = (
        "arn:aws:s3:::dev-ta-platform-dev-datasets/test/integration-tests/100k_with_filter_fields_epoc_2023-11-08/"
    )
    credentials = AWSCredentials(role_arn)
    bucket = TEST_DATASET_S3_BUCKET
    prefix = TEST_DATASET_S3_PREFIX
    glob = "*.csv"

    source = BatchS3Files(bucket, credentials, glob, prefix)

    # required fields
    entity_id = 0
    timestamp = 1
    longitude = 2
    latitude = 3

    # extra fields
    ipv4 = 4
    age = 5
    home_ipv4 = 6
    route_id = 7
    credit_card_provider = 8
    transportation_mode = 9

    csv_format = CSVFormat(
        entity_id=entity_id,
        timestamp=timestamp,
        longitude=longitude,
        latitude=latitude,
        ipv4=ipv4,
        age=age,
        home_ipv4=home_ipv4,
        route_id=route_id,
        credit_card_provider=credit_card_provider,
        transportation_mode=transportation_mode,
    )

    report = dfi.ingest.put_batch(dataset_id=dataset_id, source=source, file_format=csv_format, dry_run=False)

    assert isinstance(report, dict)
    assert report["invalidCount"] == 0
    value_store.import_batch_id = report["id"]


@pytest.mark.order(3)
def test_batch_url_files_dry_run(dataset_id: str, s3_presigner: S3URLPresigner) -> None:
    """Known to error with the following pattern:
    - 1st query -> all OK
        - 2nd query within <5 seconds -> all OK
        - 2nd query after >5 seconds -> always error
            - 3rd query after error -> always OK

    See [DFIS-1478](https://excession.atlassian.net/browse/DFIS-1478?atlOrigin=eyJpIjoiYTUxYjk4ZjAwOWU2NGU5OWFlMjYyODZlOTVhNWJlOGYiLCJwIjoiaiJ9)
    """
    dfi = Client(TOKEN, IMPORT_URL)

    prefix = TEST_DATASET_S3_PREFIX
    signed_urls = s3_presigner.generate_presigned_urls(prefix, ".csv", expiration=5)
    source = BatchURLFiles(signed_urls)

    # required fields
    entity_id = 0
    timestamp = 1
    longitude = 2
    latitude = 3

    # extra fields
    ipv4 = 4
    age = 5
    home_ipv4 = 6
    route_id = 7
    credit_card_provider = 8
    transportation_mode = 9

    csv_format = CSVFormat(
        entity_id=entity_id,
        timestamp=timestamp,
        longitude=longitude,
        latitude=latitude,
        ipv4=ipv4,
        age=age,
        home_ipv4=home_ipv4,
        route_id=route_id,
        credit_card_provider=credit_card_provider,
        transportation_mode=transportation_mode,
    )

    report = dfi.ingest.put_batch(dataset_id=dataset_id, source=source, file_format=csv_format, dry_run=True)

    if report["status"] == "error":
        _logger.error(report)

    assert isinstance(report, dict)
    assert report["status"] == "success"


@pytest.mark.order(4)
def test_batch_url_files(dataset_id: str, s3_presigner: S3URLPresigner, value_store: ValueStore) -> None:
    """Known bug where Import API dies with the following:
    requests.exceptions.ConnectionError: HTTPConnectionPool(host='dfi-import-api', port=8080): Max retries exceeded with url: /v1/import/batch/860708b6-30ed-4aa4-bafd-71ab5874bf46/status (Caused by NameResolutionError("<urllib3.connection.HTTPConnection object at 0xffff8f84e890>: Failed to resolve 'dfi-import-api' ([Errno -2] Name or service not known)"))

    Workaround: restart container in dev-env
    """
    dfi = Client(TOKEN, IMPORT_URL)

    prefix = TEST_DATASET_S3_PREFIX

    signed_urls = s3_presigner.generate_presigned_urls(prefix, ".csv", expiration=30)
    source = BatchURLFiles(signed_urls)

    # required fields
    entity_id = 0
    timestamp = 1
    longitude = 2
    latitude = 3

    # extra fields
    ipv4 = 4
    age = 5
    home_ipv4 = 6
    route_id = 7
    credit_card_provider = 8
    transportation_mode = 9

    csv_format = CSVFormat(
        entity_id=entity_id,
        timestamp=timestamp,
        longitude=longitude,
        latitude=latitude,
        ipv4=ipv4,
        age=age,
        home_ipv4=home_ipv4,
        route_id=route_id,
        credit_card_provider=credit_card_provider,
        transportation_mode=transportation_mode,
    )

    report = dfi.ingest.put_batch(dataset_id=dataset_id, source=source, file_format=csv_format, dry_run=False)
    assert isinstance(report, dict)

    # store the import batch id for following tests
    value_store.import_batch_id = report["id"]

    # Poll until import finished (~4 seconds)
    status = dfi.ingest.get_batch_status(value_store.import_batch_id)
    while status[0]["status"] not in ["finished", "error"]:
        time.sleep(1)
        status = dfi.ingest.get_batch_status(value_store.import_batch_id)

    assert isinstance(status, list)
    assert status[0]["invalidCount"] == 0
    assert status[0]["insertCount"] == 99_999


@pytest.mark.order(5)
def test_get_batch_status(import_batch_id: str) -> None:
    dfi = Client(TOKEN, IMPORT_URL)

    status = dfi.ingest.get_batch_status(import_batch_id)

    assert isinstance(status, list)


@pytest.mark.order(6)
def test_get_batch_info(import_batch_id: str) -> None:
    dfi = Client(TOKEN, IMPORT_URL)

    info = dfi.ingest.get_batch_info(import_batch_id)

    assert isinstance(info, dict)


@pytest.mark.order(7)
def test_update_batch_status(dataset_id: str, s3_presigner: S3URLPresigner) -> None:
    dfi = Client(TOKEN, IMPORT_URL)

    prefix = TEST_DATASET_S3_PREFIX

    signed_urls = s3_presigner.generate_presigned_urls(prefix, ".csv", expiration=30)
    source = BatchURLFiles(signed_urls)

    # required fields
    entity_id = 0
    timestamp = 1
    longitude = 2
    latitude = 3

    # extra fields
    ipv4 = 4
    age = 5
    home_ipv4 = 6
    route_id = 7
    credit_card_provider = 8
    transportation_mode = 9

    csv_format = CSVFormat(
        entity_id=entity_id,
        timestamp=timestamp,
        longitude=longitude,
        latitude=latitude,
        ipv4=ipv4,
        age=age,
        home_ipv4=home_ipv4,
        route_id=route_id,
        credit_card_provider=credit_card_provider,
        transportation_mode=transportation_mode,
    )

    report = dfi.ingest.put_batch(dataset_id=dataset_id, source=source, file_format=csv_format, dry_run=False)

    import_batch_id = report["id"]

    # Start import and immediately abort
    status = "aborted"
    info = dfi.ingest.update_batch_status(import_batch_id, status)  # pylint: disable=protected-access

    assert isinstance(info, dict)


@pytest.mark.order(8)
def test_batch_s3_files_raises_not_implemented_error(dataset_id: str) -> None:
    dfi = Client(TOKEN, IMPORT_URL)

    # AWS Credentials
    role_arn = (
        "arn:aws:s3:::dev-ta-platform-dev-datasets/test/integration-tests/100k_with_filter_fields_epoc_2023-11-08/"
    )
    credentials = AWSCredentials(role_arn)
    bucket = TEST_DATASET_S3_BUCKET
    prefix = TEST_DATASET_S3_PREFIX
    glob = "*.csv"

    source = BatchS3Files(bucket, credentials, glob, prefix)

    # required fields
    entity_id = 0
    timestamp = 1
    longitude = 2
    latitude = 3

    # extra fields
    ipv4 = 4
    age = 5
    home_ipv4 = 6
    route_id = 7
    credit_card_provider = 8
    transportation_mode = 9

    csv_format = CSVFormat(
        entity_id=entity_id,
        timestamp=timestamp,
        longitude=longitude,
        latitude=latitude,
        ipv4=ipv4,
        age=age,
        home_ipv4=home_ipv4,
        route_id=route_id,
        credit_card_provider=credit_card_provider,
        transportation_mode=transportation_mode,
    )

    with pytest.raises(NotImplementedError):
        _ = dfi.ingest.put_batch(dataset_id=dataset_id, source=source, file_format=csv_format, dry_run=False)
