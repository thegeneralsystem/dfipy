"""Module for geometry models."""

# ruff: noqa: F401, I001 (unused-import, un-sorted)
# isort: skip_file
from typing import TypeAlias

# Point needs to be imported before BBox or Polygon because it's a dependency in both.
# Rexported here for easier access.
from .point import Point
from .bbox import BBox
from .polygon import Polygon, RawCoords
