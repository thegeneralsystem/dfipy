# dfipy

[![PyPI - Version](https://img.shields.io/pypi/v/dfipy)](https://pypi.python.org/pypi/dfipy/)

`dfipy` is a library built for data scientists & analysts for data scientists & analysts. It is designed as a lightweight Python client for interacting with the General System Platform API.

Each GS Platform service is accessible via an appropriately named class:

- [Datasets](reference/services/datasets.md) - For accessing the Datasets API: create, edit, delete, and retrieve information about datasets in the GS Platform.
- [Delete](reference/services/delete.md) - Delete data from a dataset within the GS Platform.
- [Identities](reference/services/identities.md) - For accessing the Identity API: create, edit, delete, and retrieve information about identities in the GS Platform.
- [Info](reference/services/info.md) - For accessing versioning and API information.
- [Ingest](reference/services/ingest.md) - For accessing the Import API: ingest data into the GS Platform.
- [Query](reference/services/query.md) - For accessing the Query V1 API: query datasets in the GS Platform.
- [Users](reference/services/users.md) - For accessing the Users API: create, edit, delete, and retrieve information about users in the GS Platform.

Services are namespaced within the `#!python dfi.Client()`. As an example, the `#!python Info()` class is accessed via `#!python dfi.info`.

```python
from dfi import Client

dfi = Client("<token>", "<url>")
dfi.info.version()
```
