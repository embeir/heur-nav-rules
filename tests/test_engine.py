from pathlib import Path

import pytest

from nav_rules import Detection, compute_navigation, load_config


def _minimal_config():
    return {
        "version": "1.0",
        "goal_rules": {
            "goal_classes": ["person", "red-marker"],
            "min_confidence": 0.5,
        },
        "obstacle_rules": {"obstacle_classes": ["car"]},
        "sectors": {"approach_zone_height_ratio": 0.55},
        "blending": {
            "goal_weight": 0.65,
            "obstacle_bias_deg": {"left": -25, "center": 0, "right": 25},
            "heading_clamp_deg": [-40, 40],
        },
        "output": {"speed_scale_bounds": [0.2, 1.0]},
    }


def test_compute_navigation_no_detections():
    cmd = compute_navigation([], _minimal_config(), frame_wh=(320, 240))
    assert cmd.goal_visible is False
    assert cmd.selected_goal is None
    assert cmd.avoid_side in ("left", "center", "right")
    assert 0.2 <= cmd.speed_scale <= 1.0
    assert -40 <= cmd.heading_command_deg <= 40


def test_compute_navigation_goal_visible():
    detections = [
        Detection(
            label="person",
            confidence=0.9,
            center_x=200,
            center_y=120,
            area_ratio=0.05,
        ),
    ]
    cmd = compute_navigation(detections, _minimal_config(), frame_wh=(320, 240))
    assert cmd.goal_visible is True
    assert cmd.selected_goal == "person"
    assert cmd.heading_to_goal_deg != 0 or detections[0].center_x == 160


def test_compute_navigation_with_provided_obstacle_scores():
    detections = [
        Detection("person", 0.9, 160, 120, 0.03),
    ]
    obstacle_scores = {"left": 0.1, "center": 0.8, "right": 0.2}
    cmd = compute_navigation(
        detections,
        _minimal_config(),
        obstacle_scores=obstacle_scores,
        frame_wh=(320, 240),
    )
    assert cmd.obstacle_scores["center"] == 0.8
    assert cmd.avoid_side != "center"


def test_compute_navigation_empty_obstacle_scores_merges_defaults():
    """Empty user dict must not crash min(); merged with zeros."""
    cmd = compute_navigation(
        [],
        _minimal_config(),
        obstacle_scores={},
        frame_wh=(320, 240),
    )
    assert cmd.obstacle_scores == {"left": 0.0, "center": 0.0, "right": 0.0}
    assert cmd.avoid_side in ("left", "center", "right")


def test_compute_navigation_partial_obstacle_scores_filled():
    cmd = compute_navigation(
        [],
        _minimal_config(),
        obstacle_scores={"center": 0.5},
        frame_wh=(320, 240),
    )
    assert cmd.obstacle_scores["left"] == 0.0
    assert cmd.obstacle_scores["center"] == 0.5
    assert cmd.obstacle_scores["right"] == 0.0
    assert cmd.avoid_side == "left"


def test_compute_navigation_frame_wh_none_uses_unit_frame():
    cmd = compute_navigation([], _minimal_config(), frame_wh=None)
    assert cmd.goal_visible is False
    assert -40 <= cmd.heading_command_deg <= 40


def test_goal_priority_confidence_picks_higher_conf():
    cfg = _minimal_config()
    cfg["goal_rules"]["priority"] = "confidence"
    detections = [
        Detection("person", 0.6, 50, 120, 0.2),
        Detection("person", 0.95, 200, 120, 0.01),
    ]
    cmd = compute_navigation(detections, cfg, frame_wh=(320, 240))
    assert cmd.selected_goal == "person"
    assert cmd.goal_confidence == 0.95


def test_goal_priority_area_picks_larger_area():
    cfg = _minimal_config()
    cfg["goal_rules"]["priority"] = "area"
    detections = [
        Detection("person", 0.9, 50, 120, 0.01),
        Detection("person", 0.9, 200, 120, 0.3),
    ]
    cmd = compute_navigation(detections, cfg, frame_wh=(320, 240))
    assert abs(cmd.heading_to_goal_deg - 8.75) < 1e-6


def test_speed_scale_reduced_when_center_obstacle_high():
    cfg = _minimal_config()
    cfg["blending"]["speed_scale_reduction_by_center_score"] = [
        {"threshold": 0.05, "speed_scale": 0.5},
    ]
    cmd = compute_navigation(
        [],
        cfg,
        obstacle_scores={"left": 0.0, "center": 0.9, "right": 0.0},
        frame_wh=(320, 240),
    )
    assert cmd.speed_scale == 0.5


def test_min_area_ratio_filters_small_goal():
    cfg = _minimal_config()
    cfg["goal_rules"]["min_area_ratio"] = 0.1
    detections = [Detection("person", 0.99, 160, 120, 0.02)]
    cmd = compute_navigation(detections, cfg, frame_wh=(320, 240))
    assert cmd.goal_visible is False


def test_compute_navigation_with_example_config():
    root = Path(__file__).resolve().parent.parent
    path = root / "config_examples" / "example_rules.json"
    if not path.exists():
        pytest.skip("example_rules.json not found")
    config = load_config(path)
    detections = [
        Detection("red-marker", 0.7, 260, 120, 0.04),
    ]
    cmd = compute_navigation(detections, config, frame_wh=(320, 240))
    assert cmd.goal_visible is True
    assert cmd.selected_goal == "red-marker"
