"""Integration tests for Query V0 API.

- Must run on a clean startup of dev-env (relies on pre-ingested dataset).
- Must be run before other integration tests (other integration tests truncate and load different data).
"""

import os
from datetime import datetime

from dfi import Client
from dfi.connect import Connect
from dfi.query_document_v0 import QueryDocument
from dfi.services.datasets import Datasets

TOKEN = os.environ["API_TOKEN"]
DATASET = os.environ["DATASET"]
URL = os.environ["DFI_QUERY_API_URL"]
DATASETS_API_URL = os.environ["DFI_DATASETS_API_URL"]


def test_filter_field_entities() -> None:
    """Check filter field query for entities with and without filter fields don't match"""
    dataset_client = Datasets(conn=Connect(api_token=TOKEN, base_url=DATASETS_API_URL))
    datasets = dataset_client.find()
    dataset = next((x for x in datasets if x["id"] == DATASET), None)
    dataset_id = dataset["id"]

    query_client = Client(api_token=TOKEN, base_url=URL)
    doc = QueryDocument()
    filters_dict = dict(creditCardProvider=dict(eq="solo"))
    doc.add_filter_fields_from_dict(fields_dict=filters_dict)
    entites_no_filter = query_client.get.entities(dataset_id=dataset_id)
    entities_with_filter = query_client.get.entities(dataset_id=dataset_id, filter_fields=filters_dict)
    assert len(entites_no_filter) != len(entities_with_filter)

    if len(datasets) == 0:
        raise ValueError(f"No datasets found with bounds: name={DATASET}, limit={1}")


def test_filter_field_records() -> None:
    """Check filter field query for entities with and without filter fields don't match"""
    dataset_client = Datasets(conn=Connect(api_token=TOKEN, base_url=DATASETS_API_URL))
    datasets = dataset_client.find()
    dataset = next((x for x in datasets if x["id"] == DATASET), None)
    dataset_id = dataset["id"]

    query_client = Client(api_token=TOKEN, base_url=URL)
    doc = QueryDocument()
    filters_dict = dict(transportationMode=dict(eq="walking"))
    doc.add_filter_fields_from_dict(fields_dict=filters_dict)
    random_entity = query_client.get.entities(dataset_id=dataset_id, filter_fields=filters_dict)
    records_output = query_client.get.records(dataset_id=dataset_id, entities=random_entity, add_payload_as_json=True)
    records_with_filter = query_client.get.records(
        dataset_id=dataset_id, entities=random_entity, filter_fields=filters_dict
    )

    assert len(records_output) != len(records_with_filter)
    if len(datasets) == 0:
        raise ValueError(f"No datasets found with bounds: name={DATASET}, limit={1}")


def test_entities_with_polygon_no_filters() -> None:
    query_client = Client(api_token=TOKEN, base_url=URL)
    vertices = [
        [-0.12311972687430739, 51.522236919249934],
        [-0.055372356569336034, 51.5287331777422],
        [-0.01943468343222321, 51.479761804458775],
        [-0.1629474652304168, 51.51029951729288],
        [-0.12311972687430739, 51.522236919249934],
    ]
    entities = query_client.get.entities(dataset_id=DATASET, polygon=vertices)
    assert len(entities) > 0


def test_entities_with_polygon_and_filter_fields() -> None:
    query_client = Client(api_token=TOKEN, base_url=URL)
    vertices = [
        [-0.12311972687430739, 51.522236919249934],
        [-0.055372356569336034, 51.5287331777422],
        [-0.01943468343222321, 51.479761804458775],
        [-0.1629474652304168, 51.51029951729288],
        [-0.12311972687430739, 51.522236919249934],
    ]
    filters_dict = dict(transportationMode=dict(eq="walking"))

    entities = query_client.get.entities(dataset_id=DATASET, polygon=vertices)

    filtered_entities = query_client.get.entities(dataset_id=DATASET, polygon=vertices, filter_fields=filters_dict)

    assert len(entities) > len(filtered_entities)


def test_entities_with_polygon_and_time_filter() -> None:
    query_client = Client(api_token=TOKEN, base_url=URL)
    vertices = [
        [-0.12311972687430739, 51.522236919249934],
        [-0.055372356569336034, 51.5287331777422],
        [-0.01943468343222321, 51.479761804458775],
        [-0.1629474652304168, 51.51029951729288],
        [-0.12311972687430739, 51.522236919249934],
    ]
    start_time = datetime(2021, 10, 26, 10, 46, 13, 439985)
    end_time = datetime(2023, 10, 26, 12, 46, 13, 439989)
    entities = query_client.get.entities(dataset_id=DATASET, polygon=vertices, time_interval=(start_time, end_time))

    assert len(entities) > 0
