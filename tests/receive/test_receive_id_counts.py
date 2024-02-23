"""Tests for _receive_unique_id_counts."""

# mypy: disable-error-code="arg-type"
import logging

import pytest
from _pytest.python_api import RaisesContext
from sseclient import SSEClient

from dfi import Client
from dfi.errors import (
    DFIResponseError,
    EventsMissedError,
    NoEventsRecievedError,
    NoFinishMessageReceivedError,
    UnkownMessageReceivedError,
)

_logger = logging.getLogger(__name__)


#########################
# Error Conditions
#########################
@pytest.mark.parametrize(
    "client,expectation",
    [
        pytest.param(
            SSEClient([b'event: unknown_event\nmessageCount: 1\ndata: [["aaa", 1]]\n\n']),
            pytest.raises(UnkownMessageReceivedError),
            id="UnkownMessageReceivedError",
        ),
        pytest.param(SSEClient([]), pytest.raises(NoEventsRecievedError), id="NoEventsRecievedError"),
        pytest.param(
            SSEClient([b'messageCount: 1\ndata: [["aaa", 1]]\n\n']),
            pytest.raises(NoFinishMessageReceivedError),
            id="NoFinishMessageReceivedError",
        ),
        pytest.param(
            SSEClient([b'event: finish\ndata: {"messageCount": 2}\n\n']),
            pytest.raises(EventsMissedError),
            id="EventsMissedError",
        ),
        pytest.param(
            SSEClient([b'event: queryError\nmessageCount: 1\ndata: {"error": "test error"}\n\n']),
            pytest.raises(DFIResponseError),
            id="DFIResponseError",
        ),
    ],
)
def test_receive_unique_id_counts_error_conditions(
    dfi: Client,
    client: SSEClient,
    expectation: RaisesContext,
) -> None:
    """Test _receive_ids errors are raised."""
    with expectation:
        _ = dfi.query._receive_unique_id_counts(client)


#########################
# Normal Conditions
#########################
@pytest.mark.parametrize(
    "client,expected",
    [
        pytest.param(SSEClient([b'event: finish\ndata: {"messageCount": 0}\n\n']), {}, id="finish with no messages"),
        pytest.param(
            SSEClient([b'event: message\ndata: [["aaa", 1]]\n\n', b'event: finish\ndata: {"messageCount": 1}\n\n']),
            {"aaa": 1},
            id="one message event",
        ),
        pytest.param(
            SSEClient(
                [
                    b'data: [["aaa", 1]]\n\n',
                    b'data: [["bbb", 2], ["ccc", 3]]\n\n',
                    b'event: finish\ndata: {"messageCount": 2}\n\n',
                ]
            ),
            {"aaa": 1, "bbb": 2, "ccc": 3},
            id="multiple events sum",
        ),
    ],
)
def test_receive_unique_id_counts(
    dfi: Client,
    client: SSEClient,
    expected: dict[str, int],
) -> None:
    """Test _receive_ids works as intended."""
    unique_id_counts = dfi.query._receive_unique_id_counts(client)
    assert unique_id_counts == expected
