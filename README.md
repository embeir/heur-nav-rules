# heur-nav-rules

`heur-nav-rules` is a Python library that converts vision detections into a simple navigation command.

Input: detections + rules JSON  
Output: heading + speed scale (+ diagnostics)

## Install

```bash
pip install heur-nav-rules
```

For local development:

```bash
pip install -e ".[dev]"
```

## Usage

```python
from pathlib import Path
from nav_rules import load_config, compute_navigation, Detection

config = load_config(Path("config_examples/example_rules.json"))
detections = [
    Detection(label="person", confidence=0.9, center_x=160, center_y=120, area_ratio=0.05),
]
cmd = compute_navigation(detections, config, frame_wh=(320, 240))
print(cmd.heading_command_deg, cmd.speed_scale, cmd.goal_visible)
```

## What you provide

- **Detections**: `label`, `confidence`, `center_x`, `center_y`, optional `area_ratio`, `source`.
- **Config**: rules JSON (goal classes, obstacle classes, sectors, blending).
- Details: [docs/api.md](docs/api.md), [docs/rules_format.md](docs/rules_format.md).

## What you get

`NavigationCommand` with:
- `heading_command_deg`
- `speed_scale`
- `avoid_side`
- `goal_visible`
- `selected_goal`
- `heading_to_goal_deg`
- `obstacle_scores`

Map this output to MAVLink, ArduPilot, PX4, or your own controller.

## Rule editor

A GUI lets you create and edit rules without writing JSON by hand. Run the editor, fill the form (goal classes, obstacle classes, blending, etc.), then save to generate a rules JSON file.

```bash
pip install ".[gui]"
nav-rules-edit                    # new config (defaults)
nav-rules-edit path/to/rules.json # open and edit existing
# or
python -m nav_rules.gui [path]
```

In the window: use **Open** to load a JSON file, **Import** to load rules and merge with defaults for missing fields (useful when fixing or upgrading existing rules), **New** to reset to defaults, **Validate** to check the form, and **Save as JSON...** to write the config. See [docs/editor.md](docs/editor.md) for the workflow.

## License

MIT. See [LICENSE](LICENSE).
