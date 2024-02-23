"""Allows access to submodules from dfi.<module>."""

from __future__ import annotations

from importlib.metadata import version

__version__ = version("dfipy")

from .client import Client  # noqa: F401 (unused-import)
