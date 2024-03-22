"""Configuration for receive test fixtures."""

import pytest

from dfi import Client


@pytest.fixture(name="dfi", scope="module")
def get_dfi_client() -> Client:
    return Client("token", "www.test.com")
