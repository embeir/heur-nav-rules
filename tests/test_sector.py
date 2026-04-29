"""Tests for sector / obstacle scoring."""

from nav_rules.detection import Detection
from nav_rules.sector import obstacle_scores_from_detections


def test_obstacle_scores_zero_dimensions():
    d = [Detection("car", 0.9, 50, 200, 0.1)]
    out = obstacle_scores_from_detections(d, ["car"], 0.0, 240.0, 0.55)
    assert out == {"left": 0.0, "center": 0.0, "right": 0.0}


def test_obstacle_scores_negative_width_uses_safe_defaults():
    out = obstacle_scores_from_detections([], ["car"], -1.0, 100.0, 0.55)
    assert out == {"left": 0.0, "center": 0.0, "right": 0.0}


def test_obstacle_in_approach_zone_increases_sector_score():
    w, h = 300.0, 200.0
    d = [Detection("car", 0.9, w * 0.5, h * 0.9, 0.15)]
    out = obstacle_scores_from_detections(d, ["car"], w, h, 0.55)
    assert out["left"] >= 0.0 and out["center"] >= 0.0 and out["right"] >= 0.0
    assert max(out.values()) > 0.0


def test_non_obstacle_label_ignored():
    w, h = 300.0, 200.0
    d = [Detection("person", 0.9, w * 0.5, h * 0.9, 0.2)]
    out = obstacle_scores_from_detections(d, ["car"], w, h, 0.55)
    assert out == {"left": 0.0, "center": 0.0, "right": 0.0}
