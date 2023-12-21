"""Integration tests for the Datasets module
Since these tests have side effects on the Datasets API service and some rely on the state
of the service, the order in which the tests are run matters.  We use pytest-order to specify 
the order in qhich tests are run.  
"""
import json
import os

import pyarrow as pa
import pytest

from dfi import Client

TOKEN = os.environ["API_TOKEN"]
URL = os.environ["DFI_DATASETS_API_URL"]
DATASET_NAME = "test-0"


@pytest.fixture(name="dataset_id")
def get_dataset_id() -> str:
    dfi = Client(TOKEN, URL)

    datasets = dfi.datasets.find()
    dataset = next((x for x in datasets if x["name"] == DATASET_NAME), None)
    if not dataset:
        raise ValueError(f"No datasets found with name {DATASET_NAME}")
    return dataset["id"]


@pytest.mark.order(1)
def test_create_dataset() -> None:
    with open("integration_tests/datasets/dataset_0.json", "r", encoding="utf-8") as fp:
        dataset = json.load(fp)

    dfi = Client(TOKEN, URL)

    created_dataset = dfi.datasets.create(dataset)

    assert isinstance(created_dataset, dict)
    assert dataset["name"] == created_dataset["name"]


@pytest.mark.order(2)
def test_find() -> None:
    dfi = Client(TOKEN, URL)

    name = DATASET_NAME
    limit = 1
    datasets = dfi.datasets.find(name=name, limit=limit)

    assert len(datasets) == 1
    assert datasets[0]["name"] == name


@pytest.mark.order(3)
def test_find_by_id(dataset_id: str) -> None:
    dfi = Client(TOKEN, URL)

    dataset = dfi.datasets.find_by_id(dataset_id=dataset_id)

    assert isinstance(dataset, dict)
    assert dataset["id"] == dataset_id


@pytest.mark.order(4)
def test_update(dataset_id: str) -> None:
    with open("integration_tests/datasets/dataset_0.json", "r", encoding="utf-8") as fp:
        dataset = json.load(fp)

    dfi = Client(TOKEN, URL)

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
def test_get_permissions(dataset_id: str) -> None:
    dfi = Client(TOKEN, URL)

    permissions = dfi.datasets.get_permissions(dataset_id=dataset_id)

    assert isinstance(permissions, list)


@pytest.mark.order(6)
def test_add_permissions(dataset_id: str) -> None:
    dfi = Client(TOKEN, URL)

    permissions = [{"type": "writer", "scope": "identity", "identityId": "123"}]
    updated_permissions = dfi.datasets.add_permissions(dataset_id=dataset_id, permissions=permissions)

    for permission in permissions:
        assert permission in updated_permissions


@pytest.mark.order(7)
def test_delete_permissions(dataset_id: str) -> None:
    dfi = Client(TOKEN, URL)

    permissions = [{"type": "reader", "scope": "all"}]
    deleted_permissions = dfi.datasets.delete_permissions(dataset_id=dataset_id, permissions=permissions)

    assert permissions == deleted_permissions


@pytest.mark.order(8)
def test_get_my_permissions(dataset_id: str) -> None:
    dfi = Client(TOKEN, URL)

    permissions = dfi.datasets.get_my_permissions(dataset_id=dataset_id)

    assert isinstance(permissions, dict)


@pytest.mark.order(9)
def test_get_schema_as_json(dataset_id: str) -> None:
    dfi = Client(TOKEN, URL)

    schema = dfi.datasets.get_schema(dataset_id=dataset_id, media_type="json")
    assert isinstance(schema, dict)


@pytest.mark.order(10)
def test_get_schema_as_feather(dataset_id: str) -> None:
    dfi = Client(TOKEN, URL)

    schema = dfi.datasets.get_schema(dataset_id=dataset_id, media_type="feather")
    assert isinstance(schema, pa.Schema)


@pytest.mark.order(11)
def test_add_enums(dataset_id: str) -> None:
    dfi = Client(TOKEN, URL)

    metadata_enums = {
        "plantCultivar": {
            "type": "enum",
            "values": [
                "kale",
                "kohlrabi",
                "mustard",
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Cras fermentum odio eu feugiat pretium nibh ipsum consequat. Mauris nunc congue nisi vitae suscipit. Imperdiet massa tincidunt nunc pulvinar sapien. Cras tincidunt lobortis feugiat vivamus at augue eget. Blandit aliquam etiam erat velit scelerisque in dictum non. Feugiat in ante metus dictum at. Suspendisse sed nisi lacus sed viverra tellus in hac habitasse. Tellus id interdum velit laoreet id donec ultrices tincidunt arcu. Vitae sapien pellentesque habitant morbi tristique senectus. Nibh venenatis cras sed felis eget velit aliquet sagittis id. Nullam non nisi est sit amet facilisis magna.
                Nibh ipsum consequat nisl vel pretium. Lorem ipsum dolor sit amet consectetur adipiscing. Blandit massa enim nec dui nunc mattis enim. Lectus urna duis convallis convallis tellus id interdum velit laoreet. Integer enim neque volutpat ac. Accumsan in nisl nisi scelerisque eu ultrices vitae auctor eu. Ornare arcu dui vivamus arcu felis bibendum ut. In nibh mauris cursus mattis. Dui vivamus arcu felis bibendum ut tristique et. Lacus vel facilisis volutpat est velit egestas dui id. Est sit amet facilisis magna etiam tempor orci eu. Vitae turpis massa sed elementum tempus egestas sed sed risus. Tortor at risus viverra adipiscing at in tellus. Et egestas quis ipsum suspendisse ultrices.
                Arcu cursus euismod quis viverra. Diam ut venenatis tellus in metus vulputate eu scelerisque felis. Porttitor eget dolor morbi non arcu. Convallis tellus id interdum velit. Fames ac turpis egestas maecenas pharetra. Viverra maecenas accumsan lacus vel facilisis volutpat est velit egestas. Eleifend donec pretium vulputate sapien nec sagittis aliquam malesuada bibendum. Risus ultricies tristique nulla aliquet enim. Id neque aliquam vestibulum morbi. Odio ut enim blandit volutpat maecenas volutpat blandit aliquam. Egestas sed tempus urna et pharetra. Massa tincidunt nunc pulvinar sapien. Ut sem viverra aliquet eget sit amet tellus cras adipiscing. Enim nunc faucibus a pellentesque sit. Commodo elit at imperdiet dui accumsan sit amet. Odio ut enim blandit volutpat maecenas volutpat. Libero nunc consequat interdum varius sit amet. Aenean euismod elementum nisi quis eleifend quam adipiscing vitae proin.
                Mauris nunc congue nisi vitae suscipit tellus mauris a. Leo integer malesuada nunc vel risus. Aliquam id diam maecenas ultricies mi eget mauris pharetra. Convallis aenean et tortor at risus viverra adipiscing at in. Nunc pulvinar sapien et ligula ullamcorper malesuada proin libero. Urna id volutpat lacus laoreet non curabitur gravida. Id consectetur purus ut faucibus pulvinar. Aliquam ut porttitor leo a diam. Euismod nisi porta lorem mollis aliquam ut. Lectus nulla at volutpat diam ut. In nibh mauris cursus mattis molestie a iaculis. Commodo nulla facilisi nullam vehicula ipsum a. Aliquet enim tortor at auctor urna nunc id cursus. Porttitor rhoncus dolor purus non enim praesent elementum facilisis.
                Ultricies mi eget mauris pharetra et ultrices. Mi quis hendrerit dolor magna eget. At consectetur lorem donec massa sapien faucibus. Odio euismod lacinia at quis risus. Tempus egestas sed sed risus pretium quam vulputate. Aliquet bibendum enim facilisis gravida. Enim neque volutpat ac tincidunt vitae semper quis lectus. Nisl suscipit adipiscing bibendum est ultricies integer quis. Consectetur lorem donec massa sapien faucibus et molestie ac feugiat. Arcu felis bibendum ut tristique et egestas quis. Eget nunc scelerisque viverra mauris in aliquam sem fringilla.""",
            ],
            "nullable": True,
        },
    }
    schema = dfi.datasets.add_enums(dataset_id=dataset_id, metadata_enums=metadata_enums)

    assert isinstance(schema, dict)


@pytest.mark.order(12)
def test_delete(dataset_id: str) -> None:
    dfi = Client(TOKEN, URL)

    dfi.datasets.delete(dataset_id=dataset_id)
