"""Module for geometry models."""

# ruff: noqa: F401, I001 (unused-import, un-sorted)
# isort: skip_file
from typing import TypeAlias

# Point needs to be imported before BBox or Polygon because it's a dependency in both.
# Rexported here for easier access.
from .point import Point
from .bbox import BBox
from .polygon import Polygon, RawCoords

# TODO: Deprecated
PolygonOrBBox: TypeAlias = list[float] | list[RawCoords]
"""Alias for `Union[List[float], List[RawCoords]]`

- vertices - polygon vertices should follow the [GeoJSON RFC7946](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.6)
    - ex: `[[lon_1, lat_1], [lon_2, lat_2], [lon_3, lat_3], [lon_1, lat_1]]`
- bbox - bounding box should be a 2D bbox and follow the [GeoJSON RFC7946](https://datatracker.ietf.org/doc/html/rfc7946#section-5)
    - ex: `[min_lon, min_lat, max_lon, max_lat]`
"""
