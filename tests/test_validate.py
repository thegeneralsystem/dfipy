"""Unit tests for the dfi.validate module"""
import unittest
from contextlib import contextmanager
from datetime import datetime

import pandas as pd

from dfi import validate


class TestValidate(unittest.TestCase):
    """Unittesting validation methods"""

    def setUp(self) -> None:
        self.start_time = datetime.strptime("2021-01-01T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        self.end_time = datetime.strptime("2022-05-01T08:01:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")

    def tearDown(self) -> None:
        pass

    @contextmanager
    def assertNotRaises(self, exc_type: type) -> None:  # pylint: disable=C0103
        try:
            yield None
        except exc_type as exc:
            raise self.failureException(f"{exc} raised")

    def test_df_records_ok_input(self) -> None:
        df_ok = pd.DataFrame(columns=["entity_id", "latitude", "longitude", "timestamp"])
        with self.assertNotRaises(validate.DFIDataFrameColumnsNameError):
            validate.df_records(df_ok)

    def test_df_records_ok_input_more_columns(self) -> None:
        df_ok = pd.DataFrame(columns=["entity_id", "latitude", "longitude", "timestamp", "extra column"])
        with self.assertNotRaises(validate.DFIDataFrameColumnsNameError):
            validate.df_records(df_ok)

    def test_df_records_failing_input(self) -> None:
        df_not_ok = pd.DataFrame(columns=["device_id", "latitude", "longitude", "timestamp"])
        with self.assertRaises(validate.DFIDataFrameColumnsNameError):
            validate.df_records(df_not_ok)

    def test_h3_resolution_ok(self) -> None:
        with self.assertNotRaises(validate.DFIInputValueOutOfBoundError):
            validate.h3_resolution(1)
            validate.h3_resolution(15)

    def test_h3_resolution_too_big(self) -> None:
        with self.assertRaises(validate.DFIInputValueOutOfBoundError):
            validate.h3_resolution(16)

    def test_h3_resolution_too_small(self) -> None:
        with self.assertRaises(validate.DFIInputValueOutOfBoundError):
            validate.h3_resolution(0)
