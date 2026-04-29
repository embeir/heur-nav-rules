"""Sector scoring from obstacle-class detections (thirds: left, center, right)."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nav_rules.detection import Detection


def obstacle_scores_from_detections(
    detections: list[Detection],
    obstacle_classes: list[str],
    width: float,
    height: float,
    approach_zone_height_ratio: float = 0.55,
) -> dict[str, float]:
    """
    Compute obstacle score per sector (left, center, right) from detections
    whose label is in obstacle_classes. Uses bounding box area in lower
    approach zone; sectors are vertical thirds of the image.
    """
    if width <= 0 or height <= 0:
        return {"left": 0.0, "center": 0.0, "right": 0.0}

    obstacle_set = set(obstacle_classes)
    third_w = width / 3.0
    approach_y_start = height * (1.0 - approach_zone_height_ratio)

    left_area = 0.0
    center_area = 0.0
    right_area = 0.0

    for d in detections:
        if d.label not in obstacle_set:
            continue
        total_pixels = width * height
        area_pixels = d.area_ratio * total_pixels if d.area_ratio > 0 else total_pixels * 0.01
        side = max(1.0, (area_pixels ** 0.5))
        x1 = d.center_x - side / 2
        x2 = d.center_x + side / 2
        y1 = d.center_y - side / 2
        y2 = d.center_y + side / 2
        if y2 <= approach_y_start:
            continue
        y1_clip = max(y1, approach_y_start)
        y2_clip = min(y2, height)
        if y2_clip <= y1_clip:
            continue
        h = y2_clip - y1_clip
        for sx in [0, 1, 2]:
            seg_x1 = sx * third_w
            seg_x2 = (sx + 1) * third_w
            overlap_x1 = max(x1, seg_x1)
            overlap_x2 = min(x2, seg_x2)
            if overlap_x2 > overlap_x1:
                area = (overlap_x2 - overlap_x1) * h
                if sx == 0:
                    left_area += area
                elif sx == 1:
                    center_area += area
                else:
                    right_area += area

    sector_area = third_w * (height - approach_y_start)
    if sector_area <= 0:
        return {"left": 0.0, "center": 0.0, "right": 0.0}

    return {
        "left": min(1.0, left_area / sector_area),
        "center": min(1.0, center_area / sector_area),
        "right": min(1.0, right_area / sector_area),
    }
