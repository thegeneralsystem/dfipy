"""Integration tests for the Info module."""

import os

from dfi import Client

TOKEN = os.environ["API_TOKEN"]
URL = os.environ["DFI_QUERY_API_URL"]


def test_api_version() -> None:
    dfi = Client(TOKEN, URL)

    version = dfi.info.api_version()

    assert isinstance(version, str)
    assert len(version.split(".")) > 0  # major.minor.patch


# def test_product_version() -> None:
#     # TODO: figure out which service in the dev-env this endpoint lives in
#     dfi = Client(TOKEN, URL)

#     version = dfi.info.product_version()

#     assert isinstance(version, str)
#     assert len(version.split(".")) > 0  # major.minor.patch
