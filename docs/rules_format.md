# Rules JSON format

The rules config is a single JSON file that defines how detections are turned into a navigation command.

## Top-level keys

- **`version`** (string) – Config format version (e.g. `"1.0"`).

- **`goal_rules`** – Which classes are goals and how to pick the best one.
  - `goal_classes`: list of class names (e.g. `["person", "red-marker"]`).
  - `min_confidence`: number in [0, 1]; detections below this are ignored as goals.
  - `min_area_ratio`: optional; minimum area ratio for a goal.
  - `priority`: `"confidence"` | `"area"` | `"confidence_times_area"` – how to choose the best goal when several are visible.

- **`obstacle_rules`** – Which classes contribute to obstacle sector scoring.
  - `obstacle_classes`: list of class names (e.g. `["car", "truck"]`). Detections of these classes are used to compute left/center/right scores when `obstacle_scores` is not provided by the caller.

- **`sectors`** – How the image is split for obstacle scoring.
  - `mode`: `"thirds"` – three vertical columns (left, center, right).
  - `approach_zone_height_ratio`: number in (0, 1]; only the lower part of the image (e.g. 0.55 = lower 55%) is used for obstacle area.

- **`blending`** – How goal heading and obstacle avoidance are combined.
  - `goal_weight`: weight for goal heading (e.g. 0.65); obstacle bias gets (1 - goal_weight).
  - `obstacle_bias_deg`: `{"left": -25, "center": 0, "right": 25}` – heading offset in degrees when avoiding toward that sector.
  - `heading_clamp_deg`: [min, max] for final heading command (e.g. `[-40, 40]`).
  - `speed_scale_when_goal_visible`: default speed scale when a goal is visible (e.g. 0.85).
  - `speed_scale_reduction_by_center_score`: list of `{ "threshold": number, "speed_scale": number }`; if center obstacle score is above threshold, speed is reduced to at most that value.

- **`output`** – Bounds for the command.
  - `heading_bounds_deg`: [min, max].
  - `speed_scale_bounds`: [min, max] (e.g. `[0.2, 1.0]`).

See `config_examples/example_rules.json` for a full example. The schema is in `schemas/rules_schema.json`.
