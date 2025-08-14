from __future__ import annotations

import json
from typing import Any


def parse_jsonish(value: Any) -> Any:
    """If value is a JSON string, parse it; otherwise return as-is.

    Useful when reading Parquet that may have serialized dicts as JSON strings.
    """
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


