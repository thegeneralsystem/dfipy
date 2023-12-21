"""Integration tests for the User module
Since these tests have side effects on the User Management API service and some rely on the state
of the service, the order in which the tests are run matters.  We use pytest-order to specify 
the order in qhich tests are run.  

These tests don't test for correctness of the API, only for correctness of the python wrapper.
"""
import os

import pytest

from dfi import Client

TOKEN = os.environ["API_TOKEN"]
URL = os.environ["DFI_USERS_API_URL"]


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_create_token() -> None:
    dfi = Client(TOKEN, URL)

    name = "test-token"
    validity = "P1Y"
    token_info = dfi.identities.create_token(name, validity)

    assert isinstance(token_info, dict)


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_create_token"])
def test_get_tokens() -> None:
    dfi = Client(TOKEN, URL)

    tokens = dfi.identities.get_tokens(True)
    assert isinstance(tokens, list)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_create_token"])
def test_expire_token() -> None:
    dfi = Client(TOKEN, URL)

    tokens = dfi.identities.get_tokens(False)
    for token in tokens:
        if token["name"] == "test-token":
            dfi.identities.expire_token(token["id"])


@pytest.mark.order(4)
def test_get_identities() -> None:
    dfi = Client(TOKEN, URL)

    identities = dfi.identities.get_identities()
    assert isinstance(identities, list)


@pytest.mark.order(5)
def test_get_my_identity() -> None:
    dfi = Client(TOKEN, URL)

    identity = dfi.identities.get_my_identity()
    assert isinstance(identity, dict)


@pytest.mark.order(6)
@pytest.mark.dependency()
def test_create_user(test_user: dict) -> None:
    dfi = Client(TOKEN, URL)

    created_user = dfi.users.create_user(test_user)

    assert isinstance(created_user, dict)
    assert test_user["userName"] == created_user["userName"]


@pytest.mark.order(7)
@pytest.mark.dependency(depends=["test_create_user"])
def test_get_identity(test_identity_id: str) -> None:
    dfi = Client(TOKEN, URL)

    identity = dfi.identities.get_identity(test_identity_id)
    assert isinstance(identity, dict)


@pytest.mark.order(8)
@pytest.mark.dependency(depends=["test_create_user"])
def test_get_users(test_user_name: str) -> None:
    dfi = Client(TOKEN, URL)

    users = dfi.users.get_users()

    user_found = False
    for user in users:
        if user["userName"] == test_user_name:
            user_found = True
    assert user_found


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_create_user"])
def test_get_user(test_identity_id: str) -> None:
    dfi = Client(TOKEN, URL)

    user_id = dfi.identities.get_user_id(test_identity_id)
    user = dfi.users.get_user(user_id)
    assert isinstance(user, dict)


def test_get_user_id() -> None:
    dfi = Client(TOKEN, URL)

    identity_id = "user|aaaa-bbbb-cccceeee"
    expected_user_id = "aaaa-bbbb-cccceeee"

    user_id = dfi.identities.get_user_id(identity_id)
    assert user_id == expected_user_id


@pytest.mark.order(10)
@pytest.mark.dependency(depends=["test_get_user"])
def test_delete_user(test_identity_id) -> None:
    dfi = Client(TOKEN, URL)

    user_id = dfi.identities.get_user_id(test_identity_id)
    dfi.users.delete_user(user_id)


# Note: deleting the sole identity for a user makes the user unsearchable,
# which makes finding the id to then delete the user impossible.
@pytest.mark.order(11)
@pytest.mark.dependency(depends=["test_get_user"])
def test_delete_identity(test_identity_id):
    dfi = Client(TOKEN, URL)

    dfi.identities._delete_identity(test_identity_id)  # pylint: disable=protected-access
