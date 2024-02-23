(querying-data)=

# Querying Data

There are three main entry points for querying the DFI:

- `dfi.get.records()` - queries for records within the filter bounds
- `dfi.get.entities()` - queries for the unique entities within the filter bounds
- `dfi.get.records_count()` - queries for the count of records within the filter bounds

All three methods have the filter bounds `polygon` and `time_interval`. The `dfi.get.records()` and `dfi.get.records_count()` have an additional filter bound, `entities`.

:::{note}
These filter bounds are optional but at least one filter bound must be specified.
:::

:::{caution}
More restrictive filter bounds will result in a more targeted query, whereas a query with less restrictive filter bounds will result in a broader query and may return a larger result set (dependent on the distribution of the dataset).

Running `dfi.get.records()` with loose filter bounds may query for a large number of records. Ensure your machine has enough free memory to collect the data returned by the query.  
:::

## Initialization

```python
from datetime import datetime

from dfi import Client

token = "<token>"
url = "https://api.prod.generalsystem.com"

dfi = Client(token, url)
```

:::{tip}
If working in a REPL or notebook or while developing, it can be helpful to see the query progress.

```python
dfi = Client(token, url, progress_bar=True)
```

:::

## Records

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

df = dfi.get.records(
    dataset_id=dataset_id,
    polygon=vertices,
    time_interval=(start_time, end_time)
)
```

## Unique Entities

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

entities = dfi.get.entities(
    dataset_id=dataset_id,
    polygon=vertices,
    time_interval=(start_time, end_time)
)
```

## Count

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

count = dfi.get.records_count(
    dataset_id=dataset_id,
    polygon=vertices,
    time_interval=(start_time, end_time)
)
```

## Entity Records

```python
dataset_id = "<dataset id>"
entity = "01234567-89AB-CDEF-1234-0123456789AB"

df = dfi.get.records(
    dataset_id=dataset_id,
    entities=[entity],
)
```

## Filter Fields

:::{note}
See [Filter Fields](#filter-fields) for details.
:::

It is possible to filter using fields defined in the data that are not spatio temporal. To use these fields you can provide a dictionary with the name of the field you want to filter, then a dictionary with the filter operation and the value to filter by.

```python

dataset_id = "<dataset id>"
start_time = datetime(2022, 1, 1, 0, 0, 0)
end_time = datetime(2022, 1, 1, 1, 0, 0)
filters_dict = {"ipv4": {"eq": "192.168.1.254"}}
vertices = [
    [-0.1185191981562923, 51.50940914018378],
    [-0.11675363179935516, 51.507195881522705],
    [-0.11529890458942305, 51.50769890429561],
    [-0.11705203738009118, 51.50983475452347],
    [-0.1185191981562923, 51.50940914018378]
]

entities = dfi.get.entities(
    dataset_id=dataset_id,
    polygon=vertices,
    time_interval=(start_time, end_time)
    filter_fields=filters_dict
)
```
