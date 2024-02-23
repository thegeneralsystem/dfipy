"""Unit tests for the dfi.validate module."""

import unittest
from contextlib import contextmanager
from datetime import datetime


class TestValidate(unittest.TestCase):
    """Unittesting validation methods."""

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
