"""Allows access to submodules from dfi namespace."""

from __future__ import annotations

from importlib.metadata import version

__version__ = version("dfipy")

from dfi.client import Client  # noqa: F401 (unused-import)
