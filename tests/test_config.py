from pathlib import Path

import pytest

from nav_rules.config import DEFAULT_CONFIG, load_config, load_config_from_dict


def test_default_config_is_valid():
    out = load_config_from_dict(DEFAULT_CONFIG)
    assert out["version"] == "1.0"


def test_load_config_from_example():
    root = Path(__file__).resolve().parent.parent
    path = root / "config_examples" / "example_rules.json"
    if not path.exists():
        pytest.skip("example_rules.json not found")
    config = load_config(path)
    assert config["version"] == "1.0"
    assert "person" in config["goal_rules"]["goal_classes"]
    assert config["blending"]["goal_weight"] == 0.65


def test_load_config_from_dict_valid():
    config = {
        "version": "1.0",
        "goal_rules": {
            "goal_classes": ["person"],
            "min_confidence": 0.5,
        },
        "obstacle_rules": {"obstacle_classes": []},
        "sectors": {},
        "blending": {
            "goal_weight": 0.65,
            "obstacle_bias_deg": {"left": -25, "center": 0, "right": 25},
            "heading_clamp_deg": [-40, 40],
        },
        "output": {},
    }
    out = load_config_from_dict(config)
    assert out["version"] == "1.0"


def test_load_config_from_dict_invalid_raises():
    import jsonschema
    with pytest.raises(jsonschema.ValidationError):
        load_config_from_dict({"version": "1.0"})
