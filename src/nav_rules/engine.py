"""Rule engine: detections + config -> NavigationCommand."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nav_rules.detection import Detection
from nav_rules.sector import obstacle_scores_from_detections

_DEFAULT_OBSTACLE_SCORES: dict[str, float] = {"left": 0.0, "center": 0.0, "right": 0.0}


@dataclass
class NavigationCommand:
    """Output: protocol-agnostic navigation command (map to MAVLink etc.)."""

    heading_command_deg: float
    speed_scale: float
    avoid_side: str
    goal_visible: bool
    selected_goal: str | None
    heading_to_goal_deg: float
    obstacle_scores: dict[str, float]
    goal_confidence: float = 0.0


def compute_navigation(
    detections: list[Detection],
    config: dict[str, Any],
    *,
    obstacle_scores: dict[str, float] | None = None,
    frame_wh: tuple[int, int] | None = None,
) -> NavigationCommand:
    """
    Compute navigation command from detections and rules config.
    If obstacle_scores is None, compute from detections (obstacle_classes).
    frame_wh is (width, height) for normalizing centers and sector math.
    """
    goal_rules = config.get("goal_rules") or {}
    obstacle_rules = config.get("obstacle_rules") or {}
    sectors_cfg = config.get("sectors") or {}
    blending = config.get("blending") or {}
    output_cfg = config.get("output") or {}

    goal_classes = set(goal_rules.get("goal_classes") or [])
    min_conf = float(goal_rules.get("min_confidence", 0.5))
    min_area = float(goal_rules.get("min_area_ratio", 0.0))
    priority = goal_rules.get("priority") or "confidence_times_area"

    width = float(frame_wh[0]) if frame_wh and frame_wh[0] else 1.0
    height = float(frame_wh[1]) if frame_wh and frame_wh[1] else 1.0

    goal_candidates = [
        d for d in detections
        if d.label in goal_classes and d.confidence >= min_conf and d.area_ratio >= min_area
    ]

    if obstacle_scores is None:
        obstacle_classes = list(obstacle_rules.get("obstacle_classes") or [])
        approach_ratio = float(sectors_cfg.get("approach_zone_height_ratio", 0.55))
        obstacle_scores = obstacle_scores_from_detections(
            detections, obstacle_classes, width, height, approach_ratio
        )
    else:
        obstacle_scores = {**_DEFAULT_OBSTACLE_SCORES, **dict(obstacle_scores)}

    safest_sector = min(obstacle_scores, key=obstacle_scores.get)
    avoid_side = safest_sector

    goal_weight = float(blending.get("goal_weight", 0.65))
    bias = blending.get("obstacle_bias_deg") or {}
    obstacle_bias_deg = float(bias.get(safest_sector, 0))
    clamp = blending.get("heading_clamp_deg") or [-40, 40]
    clamp_min, clamp_max = float(clamp[0]), float(clamp[1])
    speed_when_goal = float(blending.get("speed_scale_when_goal_visible", 0.85))
    reduction_rules = blending.get("speed_scale_reduction_by_center_score") or []

    selected_goal = None
    heading_to_goal_deg = 0.0
    goal_visible = False
    speed_scale = 1.0
    goal_confidence = 0.0

    if goal_candidates:
        if priority == "confidence":
            goal = max(goal_candidates, key=lambda d: d.confidence)
        elif priority == "area":
            goal = max(goal_candidates, key=lambda d: d.area_ratio)
        else:
            goal = max(goal_candidates, key=lambda d: d.confidence * (1.0 + d.area_ratio))
        selected_goal = goal.label
        goal_visible = True
        goal_confidence = goal.confidence
        half_w = width / 2.0
        relative = (goal.center_x - half_w) / half_w if half_w > 0 else 0.0
        heading_to_goal_deg = max(-35, min(35, relative * 35))
        speed_scale = speed_when_goal

    center_score = obstacle_scores.get("center", 0.0)
    for rule in reduction_rules:
        if center_score > float(rule.get("threshold", 0)):
            speed_scale = min(speed_scale, float(rule.get("speed_scale", 1.0)))

    if goal_visible:
        heading_command = (heading_to_goal_deg * goal_weight) + (obstacle_bias_deg * (1.0 - goal_weight))
    else:
        heading_command = obstacle_bias_deg

    heading_command = max(clamp_min, min(clamp_max, heading_command))

    bounds = output_cfg.get("speed_scale_bounds") or [0.2, 1.0]
    speed_scale = max(float(bounds[0]), min(float(bounds[1]), speed_scale))

    return NavigationCommand(
        heading_command_deg=heading_command,
        speed_scale=speed_scale,
        avoid_side=avoid_side,
        goal_visible=goal_visible,
        selected_goal=selected_goal,
        heading_to_goal_deg=heading_to_goal_deg,
        obstacle_scores=dict(obstacle_scores),
        goal_confidence=goal_confidence,
    )
