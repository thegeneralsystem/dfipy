"""
Manages queries to the Datasets API.  Allows users to find, create, update, and delete
datasets, dataset schemas, and dataset permissions.

Tests are dependent on other test.  The order in which tests are run matters.
"""
from datetime import datetime
from typing import List, Optional, Union

import pyarrow as pa
import requests
from pyarrow import feather

from dfi.connect import Connect


class Datasets:
    """
    Class responsible handling datasets and dataset schemas.
    """

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def create(self, dataset: dict) -> dict:
        """
        Create an empty dataset.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param dataset: the dataset definition to be created.
        :return: the added dataset definition.  The `dataset_id` is returned under the `id` key.
        :example:
        ```python
        from dfi import Client

        dataset = {
          "name": "test-0",
          "description": None,
          "active": True,
          "tags": {},
          "type": "managed",
          "model": "point",
          "dataDescription": {
            "metadataSchema": {
              "plantHeight": {
                "type": "number",
                "nullable": False,
                "signed": False
              },
              "plantIPv4": {
                "type": "ip",
                "nullable": True
              },
              "plantCultivar": {
                "type": "enum",
                "nullable": True,
                "values": [
                  "broccoli",
                  "brocollini",
                  "brussel sprouts",
                  "cabbage",
                  "cauliflower",
                  "collards"
                ]
              }
            },
            "boundingBox": [-180.0, -90.0, 180.0, 90.0],
            "minDatetime": "2021-01-01T00:00:00.000Z",
            "maxDatetime": "2022-01-01T00:00:00.000Z"
          },
          "source": {
            "s3SourceUrl": "s3://test-bucket/dataset-0"
          },
          "pipeline": {
            "curationConfiguration": {}
          },
          "pii": {
            "keepPii": False,
            "piiFields": []
          },
          "storage": {
            "dataStoreType": "dfi",
            "dataStoreConnectionDetails": {
              "host": "0.0.0.0",
              "port": "1234",
              "queryTimeout": "3600000"
            }
          },
          "destination": {
            "dataStoreRetentionLength": 0
          },
          "permissions": [
            {
              "type": "reader",
              "scope": "all"
            }
          ]
        }

        dfi = Client(token, url)
        dfi.datasets.create(dataset)
        ```
        """
        with self.conn.api_post("v1/datasets", stream=False, payload=dataset) as response:
            response.raise_for_status()
            return response.json()

    def find(
        self, name: Optional[str] = None, before: Optional[datetime] = None, limit: Optional[int] = None
    ) -> List[dict]:
        """
        Find datasets.

        :param name: retrieves all datasets with `name`.
        :param before: retrieves all datasets created before `before`.
        :param limit: only return `limit` number of datasets.
        :return: a list of dataset definitions.
        :example:
        ```python
        from datetime import datetime
        from dfi import Client

        dfi = Client(token, url)

        time = datetime.fromisoformat("2023-03-31T12:50:00Z")
        dfi.datasets.find(name="London", before=time, limit=10)
        ```
        """
        if before:
            before = before.isoformat()

        params = {"name": name, "before": before, "limit": limit}

        with self.conn.api_get("v1/datasets", stream=False, params=params) as response:
            response.raise_for_status()
            return response.json()

    def find_by_id(self, dataset_id: str) -> dict:
        """
        Finds a dataset by id.

        :param dataset_id: id of the dataset to retrieve.
        :return: dataset definition.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        dfi.datasets.find_by_id(dataset_id="1234")
        ```
        """
        with self.conn.api_get(f"v1/datasets/{dataset_id}", stream=False) as response:
            response.raise_for_status()
            return response.json()

    def update(self, dataset_id: str, dataset: dict) -> dict:
        """
        Update a dataset by id.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param dataset_id: id of the dataset to update.
        :param dataset: new dataset definition.
        :return: updated dataset definition.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        dataset_id = "1234"

        dataset_update = {
            "description": "a test dataset",
            "dataDescription": {
                "minDatetime": "2020-01-01T00:00:00.000Z",
                "maxDatetime": "2021-01-01T00:00:00.000Z",
            },
        }

        dfi.datasets.update(dataset_id, dataset_update)
        ```
        """
        with self.conn.api_patch(f"v1/datasets/{dataset_id}", stream=False, payload=dataset) as response:
            response.raise_for_status()
            return response.json()

    def delete(self, dataset_id: str) -> None:
        """
        Delete a dataset by id.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param dataset_id: id of the dataset to delete.
        :return: None
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        dataset_id = "1234"
        dfi.datasets.delete(dataset_id)
        ```
        """
        with self.conn.api_delete(f"v1/datasets/{dataset_id}", stream=False) as response:
            response.raise_for_status()
            return None

    def get_permissions(self, dataset_id: str) -> dict:
        """
        Get list of permissions for this dataset.

        :param dataset_id: id of the dataset to retrieve permissions from.
        :return: list of permissions for dataset.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        dfi.datasets.get_permissions(dataset_id="1234")
        ```
        """
        with self.conn.api_get(f"v1/datasets/{dataset_id}/permissions", stream=False) as response:
            response.raise_for_status()
            return response.json()

    def add_permissions(self, dataset_id: str, permissions: List[dict]) -> dict:
        """
        Add new permissions to a dataset.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param dataset_id: id of the dataset to add permissions to.
        :param permissions: list of permissions to be added.
        :return: list of added permissions for the dataset.
        :example:

        ### I. Update permissions so anyone can read the dataset
        ```python
        from dfi import Client

        dataset_id = "1234"
        permissions = [
            {
                "type": "reader",
                "scope": "all"
            }
        ]
        dfi = Client(token, url)
        updated_permissions = dfi.datasets.add_permissions(dataset_id=dataset_id, permissions=permissions)
        ```

        ### II. Update permissions specific user has write permissions
        ```python
        from dfi import Client

        dataset_id = "1234"
        permissions = [
            {
                "type": "writer",
                "scope": "identity",
                "identityId": "user-123"
            }
        ]
        dfi = Client(token, url)
        updated_permissions = dfi.datasets.add_permissions(dataset_id=dataset_id, permissions=permissions)
        ```
        """
        with self.conn.api_post(f"v1/datasets/{dataset_id}/permissions", stream=False, payload=permissions) as response:
            response.raise_for_status()
            return response.json()

    def delete_permissions(self, dataset_id: str, permissions: List[dict]) -> dict:
        """
        Remove permissions from a dataset.  Given permission must match exactly to be removed.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param dataset_id: id of the dataset to remove permissions from.
        :param permissions: permissions to be deleted from the dataset.
        :return: list of deleted permissions from the dataset.
        :example:
        ```python
        from dfi import Client

        dataset_id = "1234"
        permissions = [{"type": "reader", "scope": "identity", "identityId": "123"}, {"type": "reader", "scope": "all"}]
        dfi = Client(token, url)
        dfi.datasets.delete_permissions(dataset_id=dataset_id, permissions=permissions)
        ```
        """
        with self.conn.api_delete(
            f"v1/datasets/{dataset_id}/permissions", stream=False, payload=permissions
        ) as response:
            response.raise_for_status()
            return response.json()

    def get_my_permissions(self, dataset_id: str) -> dict:
        """
        Get list of the current identity's permissions on a dataset.

        :param dataset_id: id of the dataset to retrieve user permissions from.
        :return: a list of user permissions for the dataset.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        dfi.datasets.get_my_permissions(dataset_id="1234")
        ```
        """
        with self.conn.api_get(f"v1/datasets/{dataset_id}/permissions/me", stream=False) as response:
            response.raise_for_status()
            return response.json()

    def get_schema(
        self, dataset_id: str, schema_type: str = "full", media_type: str = "json"
    ) -> Union[dict, pa.Schema]:
        """
        Retrieve a copy of the schema for this dataset.

        :param dataset_id: id of the dataset to retrieve schema from.
        :param schema_type: set which type of Feather schema to return.  Defaults to "full".
            - `full` - Return a full Feather schema with all fields
            - `core` - Return a Feather schema with only the core fields
            - `withMetadataId` - return a Feather schema with the core fields + metadataId field.
            - `withFilterFields` - return a Feather schema with the core fields + filter fields.
        :param media_type: (`json` or `feather`) defines the file format for the returned schema, either `"json"`
            or `"feather"`.  Defaults to `"json"`.
        :return: the dataset's schema.
        :example:

        ### Retrieve dataset schema as JSON
        ```python
        from dfi import Client

        dfi = Client(token, url)
        schema = dfi.datasets.get_schema(dataset_id="<dataset id>", schema_type="full", media_type="json")`

        ### Retrieve dataset schema as Feather bytes
        ```python
        from dfi import Client

        dfi = Client(token, url)
        schema = dfi.datasets.get_schema(dataset_id="<dataset id>", schema_type="full", media_type="feather")
        """
        schema_types = {
            "full": "full",
            "core": "core",
            "with_metadata_id": "withMetadataId",
            "with_filter_fields": "withFilterFields",
        }
        params = {"type": schema_types[schema_type]}

        headers = {
            "Authorization": f"Bearer {self.conn.api_token}",
            "Accept": "application/feather" if media_type == "feather" else "application/json",
        }
        url = f"{self.conn.base_url}/v1/datasets/{dataset_id}/schema"

        with requests.get(
            url,
            headers=headers,
            stream=False,
            params=params,
            timeout=self.conn.query_timeout,
        ) as response:
            response.raise_for_status()

            if media_type == "feather":
                buffer = memoryview(response.content)
                with pa.input_stream(buffer) as stream:
                    schema = stream.read_buffer()
                    return feather.read_table(schema).schema
            return response.json()

    def add_enums(self, dataset_id: str, metadata_enums: dict) -> dict:
        """
        Add new values to an enum field. Any new values added to fields here are merged into the existing values.

        :param dataset_id: id of the dataset to add enum values to.
        :param metadata_enums: a dictionary of metadata fields with enums values to be added to the dataset schema.
        :return: the newly updated metadata schema
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        metadata_enums = {
            "plantCultivar": {"type": "enum", "values": ["kale", "kohlrabi", "mustard"], "nullable": True},
        }
        dfi.datasets.add_enums(dataset_id="1234", metadata_enums=metadata_enums)
        ```
        """
        with self.conn.api_post(
            f"v1/datasets/{dataset_id}/schema/values", stream=False, payload=metadata_enums
        ) as response:
            response.raise_for_status()
            return response.json()
