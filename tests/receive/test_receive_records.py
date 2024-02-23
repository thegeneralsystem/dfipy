"""Tests for _receive_records."""

# mypy: disable-error-code="arg-type"

import logging

import pandas as pd
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
            SSEClient(
                [
                    b'event: unknown_event\nmessageCount: 1\ndata: {"id": "aaa", "coordinate": [0.0, 0.0], "time": "2020-01-01T00:00:00.000Z"}\n\n'
                ]
            ),
            pytest.raises(UnkownMessageReceivedError),
            id="UnkownMessageReceivedError",
        ),
        pytest.param(SSEClient([]), pytest.raises(NoEventsRecievedError), id="NoEventsRecievedError"),
        pytest.param(
            SSEClient(
                [
                    b'messageCount: 1\ndata: {"id": "aaa", "coordinate": [0.0, 0.0], "time": "2020-01-01T00:00:00.000Z"}\n\n'
                ]
            ),
            pytest.raises(NoFinishMessageReceivedError),
            id="NoFinishMessageReceivedError",
        ),
        pytest.param(
            SSEClient([b'event: finish\ndata: {"messageCount": 2}\n\n']),
            pytest.raises(EventsMissedError),
            id="NoFinishMessageReceivedError",
        ),
        pytest.param(
            SSEClient([b'event: queryError\nmessageCount: 1\ndata: {"error": "test error"}\n\n']),
            pytest.raises(DFIResponseError),
            id="DFIResponseError",
        ),
    ],
)
def test_receive_records_error_conditions(
    dfi: Client,
    client: SSEClient,
    expectation: RaisesContext,
) -> None:
    """Test _receive_points errors are raised."""
    with expectation:
        _ = dfi.query._receive_records(client)


#########################
# Normal Conditions
#########################
@pytest.mark.parametrize(
    "client,expected",
    [
        pytest.param(
            SSEClient([b'event: finish\ndata: {"messageCount": 0}\n\n']),
            pd.DataFrame(columns=["id", "coordinate", "time"]),
            id="finish with no messages",
        ),
        pytest.param(
            SSEClient([b"event: message\ndata: []\n\n", b'event: finish\ndata: {"messageCount": 1}\n\n']),
            pd.DataFrame(columns=["id", "coordinate", "time"]),
            id="one message event with no data",
        ),
        pytest.param(
            SSEClient(
                [
                    b'event: message\ndata: [{"id": "aaa", "coordinate": [0.0, 0.0], "time": "2020-01-01T00:00:00.000Z"}]\n\n',
                    b'event: finish\ndata: {"messageCount": 1}\n\n',
                ]
            ),
            pd.DataFrame([{"id": "aaa", "coordinate": [0.0, 0.0], "time": pd.to_datetime("2020-01-01T00:00:00.000Z")}]),
            id="one message event",
        ),
        pytest.param(
            SSEClient(
                [
                    b'data: [{"id": "aaa", "coordinate": [0.0, 0.0], "time": "2020-01-01T00:00:00.000Z"}]\n\n',
                    b'data: [{"id": "bbb", "coordinate": [0.0, 0.0], "time": "2020-01-01T00:00:00.000Z"}]\n\n',
                    b'event: finish\ndata: {"messageCount": 2}\n\n',
                ]
            ),
            pd.DataFrame(
                [
                    {"id": "aaa", "coordinate": [0.0, 0.0], "time": pd.to_datetime("2020-01-01T00:00:00.000Z")},
                    {"id": "bbb", "coordinate": [0.0, 0.0], "time": pd.to_datetime("2020-01-01T00:00:00.000Z")},
                ]
            ),
            id="multiple events sum",
        ),
    ],
)
def test_receive_records(
    dfi: Client,
    client: SSEClient,
    expected: pd.DataFrame,
) -> None:
    """Test _receive_records works as intended."""
    points = dfi.query._receive_records(client)
    pd.testing.assert_frame_equal(points, expected)
