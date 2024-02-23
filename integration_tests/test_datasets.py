"""Integration tests for the Datasets module
Since these tests have side effects on the Datasets API service and some rely on the state
of the service, the order in which the tests are run matters.  We use pytest-order to specify 
the order in qhich tests are run.  
"""
import json
import logging
import os

import pyarrow as pa
import pytest
from integration_tests.conftest import ValueStore

from dfi import Client
from dfi.validate import DFIResponseError

TOKEN = os.environ["API_TOKEN"]
DATASETS_API_URL = os.environ["DFI_DATASETS_API_URL"]
DATASET_NAME = "test-0"
DATASET_FILE = "integration_tests/datasets/datasets-dataset.json"

_logger = logging.getLogger(__name__)


@pytest.fixture(name="dataset_id", scope="module")
def get_dataset_id(value_store: ValueStore) -> str:
    return value_store.dataset_id


@pytest.fixture(name="dataset_name", scope="module")
def get_dataset_name(value_store: ValueStore) -> str:
    return value_store.dataset_name


@pytest.fixture(scope="module", autouse=True)
def setup_teardown(dataset_id: str):
    """Fixture to setup and teardown the dfi for the tests in this module.
    Setup:
        - truncate dfi
        - check dfi is empty
        - create dataset with schema
        - check it's all gucci
    Teardown:
        - delete dataset
    """
    # SETUP
    _logger.info("SETUP")
    dfi_datasets = Client(TOKEN, DATASETS_API_URL)

    # Delete existing dataset
    with open(DATASET_FILE, "r", encoding="utf-8") as fp:
        dataset = json.load(fp)
        dataset_name = dataset["name"]

    # Delete an existing dataset with the same name (useful if tests failed without proper teardown)
    try:
        existing_dataset = dfi_datasets.datasets.find(name=dataset_name, limit=1)
        if len(existing_dataset) > 0:
            dfi_datasets.datasets.delete(existing_dataset[0]["id"])
    except DFIResponseError:
        # will error if no dataset found
        pass

    # TEST CODE
    yield

    # TEARDOWN
    _logger.info("TEARDOWN")

    # Delete Dataset
    try:
        dfi_datasets.datasets.delete(dataset_id)
    except DFIResponseError:
        # will error if trying to delete an non-existant dataset
        pass

    _logger.info("COMPLETE")


@pytest.mark.order(1)
def test_create_dataset(value_store: ValueStore) -> None:
    with open(DATASET_FILE, "r", encoding="utf-8") as fp:
        dataset = json.load(fp)

    dfi = Client(TOKEN, DATASETS_API_URL)

    created_dataset = dfi.datasets.create(dataset)

    assert isinstance(created_dataset, dict)
    assert dataset["name"] == created_dataset["name"]
    value_store.dataset_name = created_dataset["name"]
    value_store.dataset_id = created_dataset["id"]


@pytest.mark.order(2)
def test_find(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)

    limit = 1
    dataset_name = value_store.dataset_name
    datasets = dfi.datasets.find(name=dataset_name, limit=limit)

    assert len(datasets) == 1
    assert datasets[0]["name"] == dataset_name


@pytest.mark.order(3)
def test_find_by_id(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    dataset = dfi.datasets.find_by_id(dataset_id=dataset_id)

    assert isinstance(dataset, dict)
    assert dataset["id"] == dataset_id


@pytest.mark.order(4)
def test_update(value_store: ValueStore) -> None:
    with open(DATASET_FILE, "r", encoding="utf-8") as fp:
        dataset = json.load(fp)

    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    description = "a test dataset"
    min_datetime = "2020-01-01T00:00:00.000Z"
    max_datetime = "2021-01-01T00:00:00.000Z"

    dataset_update = {
        "description": description,
        "dataDescription": {
            "minDatetime": min_datetime,
            "maxDatetime": max_datetime,
        },
    }

    dataset = dfi.datasets.update(dataset_id=dataset_id, dataset=dataset_update)

    assert isinstance(dataset, dict)
    assert dataset["description"] == description
    assert dataset["dataDescription"]["minDatetime"] == min_datetime
    assert dataset["dataDescription"]["maxDatetime"] == max_datetime


@pytest.mark.order(5)
def test_get_permissions(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    permissions = dfi.datasets.get_permissions(dataset_id=dataset_id)

    assert isinstance(permissions, list)


@pytest.mark.order(6)
def test_add_permissions(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    permissions = [{"type": "writer", "scope": "identity", "identityId": "123"}]
    updated_permissions = dfi.datasets.add_permissions(dataset_id=dataset_id, permissions=permissions)

    for permission in permissions:
        assert permission in updated_permissions


@pytest.mark.order(7)
def test_delete_permissions(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    permissions = [{"type": "reader", "scope": "all"}]
    deleted_permissions = dfi.datasets.delete_permissions(dataset_id=dataset_id, permissions=permissions)

    assert permissions == deleted_permissions


@pytest.mark.order(8)
def test_get_my_permissions(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    permissions = dfi.datasets.get_my_permissions(dataset_id=dataset_id)

    assert isinstance(permissions, dict)


@pytest.mark.order(9)
def test_get_schema_as_json(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    schema = dfi.datasets.get_schema(dataset_id=dataset_id, media_type="json")
    assert isinstance(schema, dict)


@pytest.mark.order(10)
def test_get_schema_as_feather(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    schema = dfi.datasets.get_schema(dataset_id=dataset_id, media_type="feather")
    assert isinstance(schema, pa.Schema)


@pytest.mark.order(11)
def test_add_enums(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    metadata_enums = {
        "plantCultivar": {
            "type": "enum",
            "values": [
                "kale",
                "kohlrabi",
                "mustard",
            ],
            "nullable": True,
        },
    }
    schema = dfi.datasets.add_enums(dataset_id=dataset_id, metadata_enums=metadata_enums)

    assert isinstance(schema, dict)


@pytest.mark.order(12)
def test_delete(value_store: ValueStore) -> None:
    dfi = Client(TOKEN, DATASETS_API_URL)
    dataset_id = value_store.dataset_id

    dfi.datasets.delete(dataset_id=dataset_id)
