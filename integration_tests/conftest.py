"""Pytest configuration file."""

import os
from dataclasses import dataclass

import pytest

from dfi import Client

TOKEN = os.environ["API_TOKEN"]
URL = os.environ["DFI_USERS_API_URL"]
TEST_USER_NAME = "iain.m.banks"


@dataclass
class ValueStore:
    """Used to store and reuse values across tests."""

    dataset_id: str | None = None
    import_batch_id: str | None = None


@pytest.fixture(name="value_store", scope="session")
def get_value_store() -> ValueStore:
    return ValueStore()


@pytest.fixture(name="test_user_name", scope="session")
def test_user_name() -> dict:
    return TEST_USER_NAME


@pytest.fixture(name="test_user", scope="session")
def test_user() -> dict:
    return {
        "userName": TEST_USER_NAME,
        "name": {"givenName": "Iain", "familyName": "Banks"},
        "emails": [{"value": f"{TEST_USER_NAME}@organization.com", "primary": True}],
        "active": True,
    }


@pytest.fixture(name="test_identity_id", scope="session")
def get_test_identity() -> str:
    dfi = Client(TOKEN, URL)

    identities = dfi.identities.get_identities()
    for identity in identities:
        if identity["name"] == TEST_USER_NAME:
            return identity["id"]

    raise ValueError(f"No user found for '{TEST_USER_NAME}'")
