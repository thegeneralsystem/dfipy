"""Pytest configuration file"""
import os

import pytest
import truststore

from dfi import Client

TOKEN = os.environ["API_TOKEN"]
URL = os.environ["DFI_USERS_API_URL"]
TEST_USER_NAME = "iain.m.banks"


def pytest_sessionstart(session):  # pylint: disable=unused-argument
    truststore.inject_into_ssl()


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
