"""Load and validate rules config from JSON against rules_schema."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

_SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
_RULES_SCHEMA_CACHE: dict[str, Any] | None = None

DEFAULT_CONFIG: dict[str, Any] = {
    "version": "1.0",
    "goal_rules": {
        "goal_classes": ["person", "red-marker"],
        "priority": "confidence_times_area",
        "min_confidence": 0.5,
        "min_area_ratio": 0,
    },
    "obstacle_rules": {
        "obstacle_classes": ["car", "truck", "tree"],
    },
    "sectors": {
        "mode": "thirds",
        "approach_zone_height_ratio": 0.55,
    },
    "blending": {
        "goal_weight": 0.65,
        "obstacle_bias_deg": {"left": -25, "center": 0, "right": 25},
        "heading_clamp_deg": [-40, 40],
        "speed_scale_when_goal_visible": 0.85,
        "speed_scale_reduction_by_center_score": [
            {"threshold": 0.2, "speed_scale": 0.45},
            {"threshold": 0.12, "speed_scale": 0.7},
        ],
    },
    "output": {
        "heading_bounds_deg": [-40, 40],
        "speed_scale_bounds": [0.2, 1.0],
    },
}


def _get_rules_schema() -> dict[str, Any]:
    """Load rules schema with caching."""
    global _RULES_SCHEMA_CACHE
    if _RULES_SCHEMA_CACHE is None:
        path = _SCHEMA_DIR / "rules_schema.json"
        if path.exists():
            _RULES_SCHEMA_CACHE = json.loads(path.read_text(encoding="utf-8"))
        else:
            _RULES_SCHEMA_CACHE = {}
    return _RULES_SCHEMA_CACHE


def load_config(path: Path | str) -> dict[str, Any]:
    """Load rules config from JSON file and validate against rules_schema.json."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = _get_rules_schema()
    if schema:
        jsonschema.validate(instance=data, schema=schema)
    return data


def load_config_from_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Validate and return rules config from a dict."""
    schema = _get_rules_schema()
    if schema:
        jsonschema.validate(instance=d, schema=schema)
    return d
