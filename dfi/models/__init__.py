"""Models module."""

from typing import Any, TypeAlias

from .query_document import QueryDocument  # noqa: F401 (unused-import)

FilterFields: TypeAlias = dict[str, dict[str, Any]]
"""Alias for `dict[str, dict[str, Any]]`"""
