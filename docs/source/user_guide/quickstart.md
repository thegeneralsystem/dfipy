(quickstart)=

# Quickstart

## Initialization

:::{note}
See section [Token Retrieval](#token-retrieval) for instructions on obtaining an API token.
:::

```python
from datetime import datetime

from dfi import Client

token = "<token>"
url = "https://api.prod.generalsystem.com"

dfi = Client(token, url)
```

## Available Datasets

:::{note}
See section [Finding Datasets](#finding-datasets) for more information on ways to search for datasets.
:::

(available-datasets)=

### Example: Available Datasets

The example below will search for all datasets visible to the user.

```python
dfi.datasets.find()
```

```python
[
    {
        'id': 'gs.dev-1',
        'name': 'dev-1',
        'description': None,
        'createdAt': '2030-01-01T00:00:00.000Z',
        'updatedAt': '2030-01-01T00:00:00.000Z',
        'active': False,
        'tags': {},
        'type': 'managed',
        'model': 'point',
        'dataDescription': {'metadataSchema': None,
        'boundingBox': None,
        'minDatetime': None,
        'maxDatetime': None},
        'pii': {'keepPii': False, 'piiFields': []},
        'destination': {'dataStoreRetentionLength': 0},
        'lastIngestAt': None,
        'fullMetadata': None
    },
    {
        'id': 'gs.dev-2',
        'name': 'dev-2',
        'description': None,
        'createdAt': '2030-01-01T00:00:00.000Z',
        'updatedAt': '2030-01-01T00:00:00.000Z',
        'active': True,
        'tags': {},
        'type': 'managed',
        'model': 'point',
        'dataDescription': {'metadataSchema': None,
        'boundingBox': None,
        'minDatetime': None,
        'maxDatetime': None},
        'pii': {'keepPii': False, 'piiFields': []},
        'destination': {'dataStoreRetentionLength': 0},
        'lastIngestAt': None,
        'fullMetadata': None
    }
]
```

## Querying Records

:::{note}
See section [Query Data](#querying-data) for more information about querying.
:::

:::{hint}
If you don't know the dataset id, use `dfi.datasets.find()` (see [Available Datasets](#available-datasets)), the value of the `id` key in the response is the dataset id.
:::

```python
dataset_id = "<dataset id>"
start_time = datetime(2022, 1, 1, 0, 0, 0)
end_time = datetime(2022, 1, 1, 1, 0, 0)
vertices = [
    [-0.1185191981562923, 51.50940914018378],
    [-0.11675363179935516, 51.507195881522705],
    [-0.11529890458942305, 51.50769890429561],
    [-0.11705203738009118, 51.50983475452347],
    [-0.1185191981562923, 51.50940914018378]
]

dfi.get.records(
    dataset_id=dataset_id,
    polygon=vertices,
    time_interval=(start_time, end_time)
)
```

```text
| entity_id                            | timestamp           | longitude| latitude |
|--------------------------------------|---------------------|----------|----------|
| f4de0783-06f2-499b-92d8-346802ba03ea | 2022-01-01 08:29:34 | -0.14424 | 51.49816 |
| f4de0783-06f2-499b-92d8-346802ba03ea | 2022-01-01 08:29:33 | -0.14464 | 51.49821 |
| 2868a2cf-006c-4d39-8555-0a8f043b3eeb | 2022-01-01 08:29:29 | -0.14504 | 51.49826 |
```
