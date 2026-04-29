# API

## Public interface

- **`nav_rules.Detection`** – Dataclass for one detection. Fields: `label`, `confidence`, `center_x`, `center_y`, `area_ratio` (optional), `source` (optional). Use `Detection.from_dict(d)` to build from a dict.

- **`nav_rules.load_config(path)`** – Load and validate rules config from a JSON file. Returns a dict. Raises `jsonschema.ValidationError` if invalid.

- **`nav_rules.load_config_from_dict(d)`** – Validate a dict against the rules schema; returns the dict. Raises if invalid.

- **`nav_rules.compute_navigation(detections, config, *, obstacle_scores=None, frame_wh=None)`** – Compute navigation command.
  - `detections`: list of `Detection` (from your model, converted to this format).
  - `config`: dict from `load_config` or equivalent.
  - `obstacle_scores`: optional `{"left": float, "center": float, "right": float}`. If omitted, scores are computed from detections whose label is in `config["obstacle_rules"]["obstacle_classes"]`.
  - `frame_wh`: optional `(width, height)` for normalizing centers and sector math.
  - Returns **`NavigationCommand`**.

- **`nav_rules.NavigationCommand`** – Dataclass result: `heading_command_deg`, `speed_scale`, `avoid_side`, `goal_visible`, `selected_goal`, `heading_to_goal_deg`, `obstacle_scores`, `goal_confidence`. Map this to MAVLink or your protocol.

## Example

```python
from pathlib import Path
from nav_rules import load_config, compute_navigation, Detection

config = load_config(Path("config_examples/example_rules.json"))
detections = [
    Detection(label="person", confidence=0.9, center_x=160, center_y=120, area_ratio=0.05),
]
cmd = compute_navigation(detections, config, frame_wh=(320, 240))
# Map cmd.heading_command_deg, cmd.speed_scale to your autopilot.
```
