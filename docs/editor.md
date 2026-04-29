# Rule editor workflow

The rule editor is a form-based GUI that produces a rules JSON file. You configure navigation rules through the interface and save to JSON; no manual JSON editing is required.

## 1. Start the editor

```bash
pip install "nav-rules[gui]"
nav-rules-edit
```

Or with an existing rules file:

```bash
nav-rules-edit path/to/rules.json
python -m nav_rules.gui path/to/rules.json
```

If you pass a path to an existing file, the editor loads it and fills the form. Otherwise you get a new config with default values.

## 2. Configure rules in the form

The window has five tabs:

- **Goal rules** – Class names to follow (e.g. person, red-marker), priority (confidence / area / confidence_times_area), min confidence, min area ratio.
- **Obstacle rules** – Class names that count as obstacles for sector scoring (e.g. car, truck).
- **Sectors** – Mode (thirds) and approach zone height ratio (lower fraction of image used for obstacles).
- **Blending** – Goal weight, obstacle bias (left/center/right degrees), heading clamp, speed scale when goal visible, and speed reduction table by center score.
- **Output** – Heading bounds and speed scale bounds for the final command.

For list fields (goal classes, obstacle classes), enter one class per line or comma-separated. The table for “speed reduction by center score” has two columns: threshold and speed_scale (one row per rule).

## 3. Validate (optional)

Click **Validate** to check that the current form values form a valid config according to the rules schema. Invalid values or missing required fields are reported in a dialog.

## 4. Save to JSON

Click **Save as JSON...**, choose the file path, and confirm. The editor builds the config from the form, validates it, and writes the JSON file. That file can be used with `load_config(path)` in your code or passed again to the editor for later edits.

## Import for fixing existing rules

When you want to fix or upgrade existing rules, use **Import...** instead of Open. Import loads the rules from a JSON file and **merges them with defaults** for any missing fields. So if your file has an older schema or is incomplete, the editor fills in the rest with default values. You can then adjust what you need and save.

- **Open...** – loads a file as-is (replaces form).
- **Import...** – loads a file and merges with defaults; useful for upgrading partial or older configs.

## Summary

1. Run the editor (with or without an existing JSON path).
2. To fix existing rules: use **Import...** to load them and fill in missing fields.
3. Adjust the form (tabs: Goal, Obstacle, Sectors, Blending, Output).
4. Optionally use **Validate** before saving.
5. Use **Save as JSON...** to write the rules file.

You can use **Open...** to load a full config, **Import...** to load and upgrade partial/older rules, and **New** to reset the form to defaults at any time.
