(dataset-management)=

# Dataset Management

:::{note}
Some methods require admin privileges. Refer to the documentation of individual methods.
:::

(creating-a-new-dataset)=

## I. Creating a New Dataset

### Defining the Dataset's Properties

When creating a dataset, you can set a list of initial permissions for who should have access to the dataset. By default, nobody can read or write from a dataset, so you should set at least some permissions. Permissions are set as an array of JSON objects.

:::{tip}
You'll have the ability to add and remove permissions post-create so don't worry if you don't have the full list.
:::

```python
dataset = {
    "name": "example-1",
    "description": "Example Dataset Definition",
    "active": True,
    "type": "managed",
    "model": "point",
    "source": {
        "s3SourceUrl": "s3://example/"
    },
    "pii": {
        "keepPii": False
    },
    "storage": {
        "dataStoreType": "dfi",
        "dataStoreConnectionDetails": {
            "host": "<dataset name>-<xxx>.tenants.dataflowindex.io",
            "port": "27487"
        }
    },
    "destination": {
        "dataStoreRetentionLength": 0
    },
    "permissions": [
        {
            "type": "reader",
            "scope": "all"
        },
        {
            "type": "writer",
            "scope": "identity",
            "identityId": "user|01234567-89AB-CDEF-0123-456789ABCDEF"
        }
    ]
}
```

Where:

- `name` - The name of the dataset to create. Should be alphanumeric plus dashes and underscores.
- `host` - The hostname of the DFI Server.
- `port` - The port of the DFI Server (typically `27487`)
- `permissions` - who has what access to the dataset. See [Permissions](#dataset-permissions) for more details.

:::{note}
Most datasets can use the remaining given property values.
:::

(creating-the-dataset)=

### Creating the Dataset

and create the dataset in the API.

```python
token = "<admin token>"
url = "<url>"

dfi = Client(token, url)

dataset = {
    "name": "example-1",
    "description": "Example Dataset Definition",
    "active": True,
    "type": "managed",
    "model": "point",
    "source": {
        "s3SourceUrl": "s3://example/"
    },
    "pii": {
        "keepPii": False
    },
    "storage": {
        "dataStoreType": "dfi",
        "dataStoreConnectionDetails": {
            "host": "<dataset name>-<xxx>.tenants.dataflowindex.io",
            "port": 27487,
            "queryTimeout": 3600000
        }
    },
    "destination": {
        "dataStoreRetentionLength": 0
    },
    "permissions": [
        {
            "type": "reader",
            "scope": "all"
        },
        {
            "type": "writer",
            "scope": "identity",
            "identityId": "user|01234567-89AB-CDEF-0123-456789ABCDEF"
        }
    ]
}

dataset = dfi.datasets.create(dataset)

dataset_id = dataset["id"]
```

:::{note}
The dataset schema is set upon creation through the `metadataSchema` key. See [Filter Fields](#filter-fields) to learn how to describe a schema. If no `metadataSchema` key is provided, the dataset will have no Filter Fields.
:::

(finding-datasets)=

## II. Finding Datasets

### Searching by Name

To find the `dataset_id` for a dataset, search for it by name.

:::{tip}
To see all available datasets to the current user run without arguments, `dfi.datasets.find()`.
:::

```python
name = "<dataset name>"
limit = 5
datasets = dfi.datasets.find(name=name, limit=limit)
```

### Searching by ID

If the `dataset_id` is known, information about the dataset can be retrieved directly.

```python
dataset_id = "<dataset id>"
dataset = dfi.datasets.find_by_id(dataset_id=dataset_id)
```

## III. Dataset Information

### Dataset Information

General information about a dataset can be retrieved by searching for the dataset.

```python
dataset_id = "gs.prod-3"
dfi.datasets.find_by_id(dataset_id=dataset_id)
```

```text
{
    'id': 'gs.prod-3',
    'name': 'prod-3',
    'description': 'This is a dataset for the instance prod-3',
    'createdAt': '2023-10-17T19:31:05.574Z',
    'updatedAt': '2023-10-17T19:31:05.574Z',
    'active': True,
    'tags': {},
    'type': 'managed',
    'model': 'point',
    'dataDescription': {
        'metadataSchema': None,
        'boundingBox': None,
        'minDatetime': None,
        'maxDatetime': None
    },
    'pii': {
        'keepPii': True,
        'piiFields': []
    },
    'destination': {
        'dataStoreRetentionLength': 0
    },
    'lastIngestAt': None,
    'fullMetadata': None
}
```

(dataset-schema-retrieval)=

### Dataset Schema Retrieval

The dataset schema can also be retrieved. This can be useful to know what additional fields are filterable. Schemas can be returned in either JSON or as Feather.

(json-schema-retrieval)=

#### JSON

```python
dataset_id = "gs.prod-3"
dfi.datasets.get_schema(dataset_id)
```

```python
{
    "IPv4":
    {
        "type": "ip",
        "nullable": True
    },
    "age":
    {
        "type": "number",
        "nullable": True
    },
    "homeIPv4":
    {
        "type": "ip",
        "nullable": True
    },
    "route":
    {
        "type": "number",
        "signed": True
    },
    "creditCardProvider":
    {
        "type": "enum",
        "values":
        [
            "american_express",
            "visa"
        ],
        "nullable": True
    },
    "transportationMode":
    {
        "type": "enum",
        "values":
        [
            "dwelling",
            "walking",
            "cycling",
            "driving"
        ]
    }
},
```

:::{hint}
A dataset with no Filter Fields will return the following valid schema:

```python
{}
```

:::

(feather-schema-retrieval)=

#### Feather

The [Feather file format](https://arrow.apache.org/docs/python/feather.html) is a portable binary file format for storing [Apache Arrow](https://arrow.apache.org/) tables or data frames. Once received, the Feather file bytes are parsed into an [Arrow schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html).

```python
dataset_id = "<dataset id>"
dfi.datasets.get_schema_by_id(dataset_id, media_type="feather")
```

```text
uid: fixed_size_binary[16] not null
timestamp: uint64 not null
longitude: double not null
latitude: double not null
altitude: double not null
metadataId: fixed_size_binary[16]
IPv4: uint32
  -- field metadata --
  $type: 'ip'
age: uint32
homeIPv4: uint32
  -- field metadata --
  $type: 'ip'
route: uint32
creditCardProvider: uint32
  -- field metadata --
  0: 'american express'
  1: 'visa'
  $type: 'enum'
transportationMode: uint32
  -- field metadata --
  0: 'dwelling'
  1: 'walking'
  2: 'cycling'
  3: 'driving'
  $type: 'enum'
```

:::{hint}
A dataset with no Filter Fields will return the following:

```python
uid: fixed_size_binary[16] not null
timestamp: uint64 not null
longitude: double not null
latitude: double not null
altitude: double not null
metadataId: fixed_size_binary[16]
```

:::

(dataset-permissions)=

## IV. Dataset Permissions

### Types of Permissions

#### Public Read Access

To give everyone in the tenant read access to a dataset (ie: marking it public), you use:

```python
{
    "permissions": { "type": "reader", "scope": "all" }
}
```

#### User Read Access to Dataset

To give a specific identity (user id) read access to a dataset, you use:

```python
{
    "permissions": { "type": "reader", "scope": "all", "identityId": "<identityIdHere>"  }
}
```

#### User Write Access to Dataset

To give a specific identity write access to a dataset, you use:

```python
{
    "permissions": { "type": "writer", "scope": "all", "identityId": "<identity id>"  }
}
```

:::{tip}
On how to retrieve an `identity_id` see:

- [Information about an Identity](#identities-information)
- [Information about Current Identity](#current-identity-information).

:::

### Changing Dataset Permissions

#### Dataset Permissions

The permissions for a dataset can be retrieved via:

```python
dataset_id = "<dataset id>"

permissions = dfi.datasets.get_permissions(dataset_id=dataset_id)
```

#### Current User Permissions

The current identity's permissions on a dataset can be retrieved via:

```python
dataset_id = "<dataset id>"

permissions = dfi.datasets.get_my_permissions(dataset_id=dataset_id)
```

#### Adding Permissions

Multiple permissions can be added by defining a list of permissions to be added onto a dataset. The method returns the new set of current permissions on the dataset.

```python
dfi = Client(token, url)

dataset_id = "<dataset id>"
permissions = [{"type": "writer", "scope": "identity", "identityId": "123"}]
updated_permissions = dfi.datasets.add_permissions(dataset_id=dataset_id, permissions=permissions)
```

#### Removing Permissions

Multiple permissions can be removed by defining a list of permissions to be deleted from a dataset. The method returns the new set of current permissions on the dataset.

```python
dataset_id = "<dataset id>"
permissions = [{"type": "writer", "scope": "identity", "identityId": "123"}]
updated_permissions = dfi.datasets.delete_permissions(dataset_id=dataset_id, permissions=permissions)
```

## V. Updating Datasets

### Updating Dataset Information

At some point, some information about the dataset will need to be updated. For example, when new data is ingested the bounding box and datetime range may need updating.

Define the dataset keys with their updated state. The return value from the `dfi.datasets.update()` method will be the new state of the updated dataset definition.

```python
dataset_update = {
    "description": "an updated description",
    "dataDescription": {
        "boundingBox": [-180.0, -90.0, 180.0, 90.0],
        "minDatetime": "2020-01-01T00:00:00.000Z",
        "maxDatetime": "2021-01-01T00:00:00.000Z",
    },
}

dataset = dfi.datasets.update(dataset_id=dataset_id, dataset=dataset_update)
```

(updating-enum-field-values)=

### Updating Enum Field Values

If a dataset has enum filter fields, at some point, the enum values may need to be updated. For example, when new data is ingested with new enum values for a filter field.

Define the metadata enums to be added to the metadata schema. The return value from the `dfi.datasets.add_enums()` method will be the newly updated metadata schema.

:::{attention}
If a value is attempted to be ingested to an `enum` field but the value is not registered in the field's schema, the ingest process will reject the record and the ingestion will keep calm and carry on.
:::

```python
dataset_id = "<dataset id>"

metadata_enums = {
    "plantCultivar": {"type": "enum", "values": ["kale", "kohlrabi", "mustard"], "nullable": True},
}

updated_metadata_schema = dfi.datasets.add_enums(dataset_id=dataset_id, metadata_enums=metadata_enums)
```
