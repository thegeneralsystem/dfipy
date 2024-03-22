"""Tests for the Info module."""

from pathlib import Path

from dfi import Client

# this assumes pytest is initiated from the root directory
ROOT_DIR = Path().cwd()
TOKEN = "xxx"
URL = "www.website.com"


def test_version() -> None:
    dfi = Client(TOKEN, URL)

    reported_version = dfi.info.version()

    assert isinstance(reported_version, str)
