"""Integration tests for instrumentation on Query V1 API.

Since these tests have side effects on the Import API service and some rely on the state
of the service, the order in which the tests are run matters.  We use pytest-order to specify
the order in qhich tests are run.

These tests don't test for correctness of the API, only for correctness of the python wrapper.
"""

import logging

import pytest

from dfi import Client

_logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "dataset_id,identity_id,before,page_size",
    [
        pytest.param(None, None, None, None, id="all None"),
        pytest.param(None, "gs.test-dataset", None, None, id="all None"),
        pytest.param(None, "user|12345", None, None, id="identity_id"),
        pytest.param(None, None, "2024-01-01T00:00:00Z", None, id="before"),
        pytest.param(None, None, None, 1, id="before"),
        pytest.param("gs.test-dataset", "user|12345", "2024-01-01T00:00:00Z", 1, id="before"),
    ],
)
def test_instrumentation(
    dfi: Client, dataset_id: str, identity_id: str | None, before: str | None, page_size: int | None
) -> None:
    _ = dfi.query.instrumentation(dataset_id=dataset_id, identity_id=identity_id, before=before, page_size=page_size)
