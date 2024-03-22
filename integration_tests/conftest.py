"""Pytest configuration file."""

import os
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

import pytest

from dfi import Client

TOKEN = os.environ["API_TOKEN"]
URL = os.environ["DFI_USERS_API_URL"]
TEST_USER_NAME = "iain.m.banks"


@dataclass
class ValueStore:
    """Used to store and reuse values across tests."""

    dataset_id: str = ""
    dataset_name: str = ""
    import_batch_id: str = ""


@pytest.fixture(name="value_store", scope="session")
def get_value_store() -> ValueStore:
    return ValueStore()


@pytest.fixture(name="test_user_name", scope="session")
def test_user_name() -> str:
    return TEST_USER_NAME


@pytest.fixture(name="test_user", scope="session")
def test_user() -> dict[str, Any]:
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
            identity_id: str = identity["id"]
            return identity_id

    raise ValueError(f"No user found for '{TEST_USER_NAME}'")


@pytest.fixture(scope="module", autouse=True)
def setup_teardown() -> Generator[Any, Any, Any]:
    # SETUP
    dfi = Client(TOKEN, URL)

    # Clears user from DB if tests fail to delete
    users = dfi.users.get_users()
    for user in users:
        if user["userName"] == TEST_USER_NAME:
            dfi.users.delete_user(user["id"])

    # TEST CODE
    yield

    # TEARDOWN

    # Clears user from DB if tests fail to delete
    users = dfi.users.get_users()
    for user in users:
        if user["userName"] == TEST_USER_NAME:
            dfi.users.delete_user(user["id"])
