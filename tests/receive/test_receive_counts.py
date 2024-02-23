"""Tests for _receive_counts, receive_ids, and receive_records."""

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
            SSEClient([b"event: unknown_event\nmessageCount: 1\ndata: 1\n\n"]),
            pytest.raises(UnkownMessageReceivedError),
            id="UnkownMessageReceivedError",
        ),
        pytest.param(SSEClient([]), pytest.raises(NoEventsRecievedError), id="NoEventsRecievedError"),
        pytest.param(
            SSEClient([b"messageCount: 1\ndata: 1\n\n"]),
            pytest.raises(NoFinishMessageReceivedError),
            id="NoFinishMessageReceivedError",
        ),
        pytest.param(
            SSEClient([b'event: finish\ndata: {"messageCount": 2}\n\n']),
            pytest.raises(EventsMissedError),
            id="EventsMissedError",
        ),
        pytest.param(
            SSEClient([b"event: queryError\nmessageCount: 1\ndata: {'error': 'test error'}\n\n"]),
            pytest.raises(DFIResponseError),
            id="DFIResponseError",
        ),
    ],
)
def test_receive_counts_error_conditions(
    dfi: Client,
    client: SSEClient,
    expectation: RaisesContext,
) -> None:
    """Test _receive_counts errors are raised."""
    with expectation:
        _ = dfi.query._receive_counts(client)


#########################
# Normal Conditions
#########################
@pytest.mark.parametrize(
    "client,expected",
    [
        pytest.param(SSEClient([b'event: finish\ndata: {"messageCount": 0}\n\n']), 0, id="finish with no messages"),
        pytest.param(
            SSEClient([b"event: message\ndata: 1\n\n", b'event: finish\ndata: {"messageCount": 1}\n\n']),
            1,
            id="one message event",
        ),
        pytest.param(
            SSEClient([b"data: 1\n\n", b"data: 4\n\n", b'event: finish\ndata: {"messageCount": 2}\n\n']),
            5,
            id="multiple events sum",
        ),
    ],
)
def test_receive_counts(
    dfi: Client,
    client: SSEClient,
    expected: int,
) -> None:
    """Test _receive_counts works as intended."""
    counts = dfi.query._receive_counts(client)
    assert counts == expected
