(filter-fields)=

# Filter Fields

Oftentimes, spatiotemporal datasets include additional fields beyond `ID`, `Timestamp`, `Latitude`, `Longitude`, `Altitude`. These additional fields can be ingested into the General System Platform as _Filter Fields_.

Filter Fields are up to 8 additional _unindexed_ fields that can be used to filter results of a query. Filter Fields have a flexible schema design to allow various types of metadata. The schema must be defined on a dataset before records are ingested. The schema can include 0-8 Filter Fields. Once the schema is specified on a dataset, the schema cannot be changed (with the exception of appending new enum values, see section on [Enums](#enums)).

:::{note}
To find what fields are available in the dataset and their type, refer to the [Datasets API guide](#dataset-management).
:::

:::{attention}
Filter Fields **are not** returned with the record in a result set. They are only used to filter a result set.
:::

## Filter Field Types

Filter Fields can be one of 3 types: `number`, `ipv4`, and `enum`. Not all types are made equal. Some types support more operators than others and some have special functionality, see the section on the type for more information. All types can be specified as either nullable (can have null values) or not nullable (cannot have null values). Within the GS Platform, all Filter Fields are mapped to 32 bits. Any conversions required are handled automatically.

:::{attention}
All data going into a Filter Field must fit within 32 bits. If a value larger than 32 bits is attempted to be ingested, the ingest process will reject the record and the ingestion will keep calm and carry on.
:::

| Type Name | Type                    | Nullable         | Supported Operators                                                                    | Examples                           | Value Range                                                                                         |
| --------- | ----------------------- | ---------------- | -------------------------------------------------------------------------------------- | ---------------------------------- | --------------------------------------------------------------------------------------------------- |
| `number`  | 32 bit signed integer   | `True` / `False` | `eq`<br/> `ne`<br/> `lt`<br/> `lte`<br/> `gt`<br/> `gte`<br/> `between`<br/> `outside` | `0`<br/> `0`<br/> `-2147483648`    | {math}`\big[ -2^{31} + 1, \space 2^{31} - 1 \big]`                                                  |
| `number`  | 32 bit unsigned integer | `True` / `False` | (same as above)                                                                        | `0`<br/> `1000`<br/> `4294967295`  | {math}`\big[0, \space 2^{32} - 1 \big]`                                                             |
| `ipv4`    | 32 bit string           | `True` / `False` | `eq`<br/> `ne`<br/>                                                                    | `"192.168.1.2"`<br/> `"127.0.0.1"` | Any valid IPv4 string in [dot-decimal notation](https://en.wikipedia.org/wiki/Dot-decimal_notation) |
| `enum`    | any                     | `True` / `False` | `eq`<br/> `ne`<br/>                                                                    | `"hello"`<br/> `"world"`           | any                                                                                                 |

(numbers)=

### Numbers

Number Filter Fields can either be signed or unsigned. All operators work with `number` types.

:::{attention}
Floating point numbers are not supported in filter fields.  
:::

#### Example: Filtering

The example below will query for all records in the dataset between 1 Jan 2022 and 1 Feb 2022, then filter for only records with `band_2 <= 30_000`, `10_000 <= band_3`, `0 <= band_4 <= 65_535`.

```python
dataset_id = "<dataset id>"
start_time = datetime(2022, 1, 1, 0, 0, 0)
end_time = datetime(2022, 2, 1, 0, 0, 0)
filters_dict = {
    "band_2": {"lt": 30_000},
    "band_3": {"gt": 10_000},
    "band_4": {"between": [0, 65_535]},
}

dfi.get.records(
    dataset_id=dataset_id,
    time_interval=(start_time, end_time)
    filter_fields=filters_dict
)
```

#### Example: Schema Specification

Numbers are described in a schema with `"type": "number"` and the `"signed"` key designates the number as either signed or unsigned. The example below describes a Filter Fields schema with 2 number fields, where `numConnections` is unsigned and `signalStrength` is signed.

```python
{
    "metadataSchema": {
        "numConnections": {
            "nullable": False,
            "signed": False,
            "type": "number"
        }
        "signalStrength": {
            "nullable": True,
            "signed": True,
            "type": "number"
        }
    }
}
```

:::{hint}
To apply the above Filter Field schema to a dataset, set the `metadataSchema` key when creating a new dataset. See [Creating the Dataset](#creating-the-dataset) for more details.
:::

(ipv4)=

### IPv4

Ipv4 Filter Field types supprt any valid IPv4 string in [dot-decimal notation](https://en.wikipedia.org/wiki/Dot-decimal_notation), e.g. `"xxx.xxx.xxx.xxx"`. All operators work with `ipv4` types.

:::{attention}
IPv6 values are not supported in Filter Fields.
:::

#### Example: Filtering

The example below will query for all records in the dataset between 1 Jan 2022 and 1 Feb 2022, then filter for only records with `ipv4 == "127.0.0.1"`.

```python
dataset_id = "<dataset id>"
start_time = datetime(2022, 1, 1, 0, 0, 0)
end_time = datetime(2022, 2, 1, 0, 0, 0)
filters_dict = {
    "ipv4": {"eq": "127.0.0.1"},
}

dfi.get.records(
    dataset_id=dataset_id,
    time_interval=(start_time, end_time)
    filter_fields=filters_dict
)
```

#### Example: Schema Specification

```python
{
    "metadataSchema": {
        "ip": {
            "type": "ip",
            "nullable": True,
        },
    }
}
```

:::{hint}
To apply the above Filter Field schema to a dataset, set the `metadataSchema` key when creating a new dataset. See [Creating the Dataset](#creating-the-dataset) for more details.
:::

(enums)=

### Enums

Enum types are intended to store categorical data fields with values that won't fit in 32 bits. Only the `eq` and `ne` operators work with `enum` types.

:::{warning}
An `enum` Filter Field should be used only for low cardinality fields.
:::

#### Example: Filtering

The example below will query for all records in the dataset between 1 Jan 2022 and 1 Feb 2022, then filter for only records with `product == "sentinel-2"`.

```python
dataset_id = "<dataset id>"
start_time = datetime(2022, 1, 1, 0, 0, 0)
end_time = datetime(2022, 2, 1, 0, 0, 0)
filters_dict = {
    "product": {"eq": "Sentinel-2"},
}

dfi.get.records(
    dataset_id=dataset_id,
    time_interval=(start_time, end_time)
    filter_fields=filters_dict
)
```

#### Example: Schema Specification

```python
{
    "metadataSchema": {
        "product": {
            "nullable": True,
            "type": "enum",
            "values": [
                "Sentinel-1",
                "Sentinel-2",
                "Sentinel-3",
                "Sentinel-4",
                "Sentinel-5 Precursor",
                "Sentinel-5",
                "Sentinel-6",
            ]
        },
    }
}
```

:::{hint}
To apply the above Filter Field schema to a dataset, set the `metadataSchema` key when creating a new dataset. See [Creating the Dataset](#creating-the-dataset) for more details.
:::

#### Example: Enum Value Updates

:::{hint}
See [Updating Enum Field Values](#updating-enum-field-values) for details on handling new enum values.
:::

## Supported Operators

| Operator  | Operation             | Inclusive | Symbolic                                                                          |
| --------- | --------------------- | --------- | --------------------------------------------------------------------------------- |
| `eq`      | Equal                 | -         | {math}`a = x_i`                                                                   |
| `neq`     | Not equal             | -         | {math}`a \neq x_i`                                                                |
| `lt`      | Less than             | false     | {math}`a < x_i`                                                                   |
| `lte`     | Less than or equal    | true      | {math}`a \le x_i`                                                                 |
| `gt`      | Greater than          | false     | {math}`a > x_i`                                                                   |
| `gte`     | Greater than or equal | true      | {math}`a \ge x_i`                                                                 |
| `between` | Between (two values)  | true      | {math}`x_i \in [a,b] \boldsymbol{\rightarrow} a \le x_i \le b`                    |
| `outside` | Outside (two values)  | true      | {math}`x_i \notin [a,b] \boldsymbol{\rightarrow} \neg \big[a \le x_i \le b \big]` |

Where:

- {math}`a` and {math}`b` are specified values to filter on
- {math}`x_i` is a value in the Filter Field being compared to the specified value(s), where {math}`x_i \in \mathbb{X}`
- {math}`\mathbb{X}` all possible values for a given Filter Field

### Single Select Operators

The single select operators `eq` and `ne` will filter results on a single value.

:::{note}
Filter Fields do not support filtering on sets of values. Only a single value per Filter Field may be used to filter results of a query.
:::

### Range Operators

The range operators `lt`, `lte`, `gt`, and `gte` will filter on a range of values. These are all _inclusive_ of the specified value.

### Multi-Range Operators

The multi-range operators `between` and `outside` will filter on a range of values. These are all _inclusive_ of the specified values.

## Nullable

In the dataset schema, each Filter Fields can be specified to allow (or disallow) null values. Null values are mapped to a 🪄 _magic number_ ✨. If a field is designated as nullable, the magic number used is the maximum value of an unsigned 32 bit integer, `4294967295` or `0xFFFFFFFF` or `0b11111111 11111111 11111111 11111111`.

### Example: Filtering

The example below will query for all records in the dataset between 1 Jan 2022 and 1 Feb 2022, then filter for only records with `ipv4 is not None`, i.e. all query results with an ip address.

```python
dataset_id = "<dataset id>"
start_time = datetime(2022, 1, 1, 0, 0, 0)
end_time = datetime(2022, 2, 1, 0, 0, 0)
filters_dict = {
    "ipv4": {"neq": None},
}

dfi.get.records(
    dataset_id=dataset_id,
    time_interval=(start_time, end_time)
    filter_fields=filters_dict
)
```

### Example: Specification

Filter Fields can be designated as nullable (may have null values) or not nullable (cannot have null values). Use the `nullable` key to specify if a field can have null values.

:::{warning}
If a null value is attempted to be ingested into a **non-nullable** field, the record will be rejected.
:::

In the example below, `numConnections` is **non-nullable** and `signalStrength` is **nullable**.

```python
{
    "metadataSchema": {
        "numConnections": {
            "nullable": False,
            "signed": False,
            "type": "number"
        }
        "signalStrength": {
            "nullable": True,
            "signed": True,
            "type": "number"
        }
    }
}
```

:::{hint}
To apply the above Filter Field schema to a dataset, set the `metadataSchema` key when creating a new dataset. See [Creating the Dataset](#creating-the-dataset) for more details.
:::

## Schemas

Dataset schemas can be specified (and requested as) either JSON or [Arrow](https://arrow.apache.org/) formats.

### JSON

JSON schemas are human-readable and simple to specify.

:::{hint}
See section [JSON Schema Retrieval](#json-schema-retrieval) for details on retrieving schemas as JSON.
:::

### Feather

Feather schemas are a binary format schema that can be specified with [pyarrow](https://arrow.apache.org/docs/python/index.html).

:::{hint}
See section [Feather Schema Retrieval](#feather-schema-retrieval) for details on retrieving schemas as Feather.
:::
