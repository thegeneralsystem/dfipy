"""
Data models for type hints.  For argument validation see `dfi.validate`.

- `Polygon` either a list of polygon vertices or bounding box.
  - vertices - polygon vertices should follow the [GeoJSON RFC7946](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.6)
    - ex: `[[lon_1, lat_1], [lon_2, lat_2], [lon_3, lat_3], [lon_1, lat_1]]`
  - bbox - bounding box should be a 2D bbox and follow the [GeoJSON RFC7946](https://datatracker.ietf.org/doc/html/rfc7946#section-5)
    - ex: `[min_lon, min_lat, max_lon, max_lat]`
- `TimeInterval` - a tuple of datetimes where the first item should be a datetime before the second item.
    - ex: `( datetime(2022, 1, 1, 0, 0,0 ), datetime(2022, 1, 1, 12, 0, 0) )`
"""
from datetime import datetime
from typing import Dict, List, NewType, Optional, Tuple, Union

# TODO: The internal type hinting of these types don't show up in the docs and makes them quite opaque.
# Can fix by using actual types (could use shapely.geometry.Polygon and shapely.geometry.box) which come with validation batteries included.
# Once the 3D Geometry library has a python wrapper this will need to use those types to validate.
Polygon = NewType("Polygon", Union[List[float], List[List[float]]])  # type: ignore
TimeInterval = NewType("TimeInterval", Tuple[Optional[datetime], Optional[datetime]])
FilterFields = NewType("FilterPredicates", Dict[str, Dict[str, any]])
