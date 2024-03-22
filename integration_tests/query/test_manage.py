"""Integration tests for unique_id_counts on Query V1 API.

Since these tests have side effects on the Import API service and some rely on the state
of the service, the order in which the tests are run matters.  We use pytest-order to specify
the order in qhich tests are run.

These tests don't test for correctness of the API, only for correctness of the python wrapper.
"""

import logging

import pytest

from dfi import Client

_logger = logging.getLogger(__name__)


@pytest.mark.order(0)
@pytest.mark.parametrize(
    "operation",
    [("truncate")],
)
def test_query_manage(dfi: Client, dataset_id: str, operation: str) -> None:
    manage_response = dfi.query.manage(
        dataset_id,
        operation=operation,
    )
    assert isinstance(manage_response, dict)
    assert manage_response["status"] == "success"
