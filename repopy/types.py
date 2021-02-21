"""Public type definitions for repopy"""

from datetime import datetime
from typing import (
    TypeVar,
    Union,
)

Field = Union[int, float, bool, str, datetime]
FIELD_TYPES = (int, float, bool, str, datetime)

EntityType = TypeVar('EntityType')
FilterType = TypeVar('FilterType')
UpdatesType = TypeVar('UpdatesType')
