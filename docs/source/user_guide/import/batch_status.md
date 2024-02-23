(import-status)=

# Import Status

Retrieves a chronological series of status updates about an import batch.

## Example

::::{tab-set}

:::{tab-item} dfipy
:sync: dfipy

```python
from dfi import Client

dfi = Client(<token>, <url>)
dfi.ingest.get_batch_status(<import_batch_id>)
```

```python
[
    {
        "id": "3c1243c4-a532-4487-9662-5655a23dec3a",
        "status": "finished",
        "insertCount": 999999999,
        "invalidCount": 0,
        "log": "2024-01-25T15:27:52.302Z INFO Starting batch job\n2024-01-25T15:27:52.308Z INFO Using 3 parallel streams\n2024-01-25T15:27:52.309Z INFO Starting import\n2024-01-25T15:27:52.310Z INFO Connected to database 'dfi-import-api' at postgres with user 'dfi-import-api-db-user'\n2024-01-25T15:27:52.321Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-000.csv\n2024-01-25T15:27:52.321Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-001.csv\n2024-01-25T15:27:52.322Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-002.csv\n2024-01-25T15:27:52.787Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-003.csv\n2024-01-25T15:27:52.789Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-004.csv\n2024-01-25T15:27:52.796Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-005.csv\n2024-01-25T15:27:53.015Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-006.csv\n2024-01-25T15:27:53.077Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-007.csv\n2024-01-25T15:27:53.177Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-008.csv\n2024-01-25T15:27:53.552Z INFO Finished batch job. Inserted: 999999999, Invalid: 0",
        "updatedAt": "2024-01-25T15:27:53.552Z",
    },
    {
        "id": "3c1243c4-a532-4487-9662-5655a23dec3a",
        "status": "started",
        "insertCount": 0,
        "invalidCount": 0,
        "log": "2024-01-25T15:27:52.302Z INFO Starting batch job\n2024-01-25T15:27:52.308Z INFO Using 3 parallel streams\n2024-01-25T15:27:52.309Z INFO Starting import",
        "updatedAt": "2024-01-25T15:27:52.312Z",
    },
    {
        "id": "3c1243c4-a532-4487-9662-5655a23dec3a",
        "status": "created",
        "insertCount": 0,
        "invalidCount": 0,
        "log": None,
        "updatedAt": "2024-01-25T15:27:52.292Z",
    },
]
```

:::
::::
