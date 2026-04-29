"""GUI rule editor: form-based editor that exports rules to JSON."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from nav_rules.config import DEFAULT_CONFIG, load_config, load_config_from_dict
from nav_rules.styles import MILITARY_STYLESHEET

_PRIORITY_OPTIONS = ("confidence", "area", "confidence_times_area")


def _parse_list_text(text: str) -> list[str]:
    """Parse comma- or newline-separated list, strip empty."""
    items = []
    for part in text.replace(",", "\n").splitlines():
        item = part.strip()
        if item:
            items.append(item)
    return items


def _format_list(items: list[str]) -> str:
    return "\n".join(items) if items else ""


def _deep_merge(default: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge override into default; nested dicts merged recursively, lists/other use override."""
    out: dict[str, Any] = dict(default)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _merge_with_defaults(config: dict[str, Any]) -> dict[str, Any]:
    """Merge imported config with defaults; missing keys get default values."""
    result: dict[str, Any] = {}
    for key in DEFAULT_CONFIG:
        default_val = DEFAULT_CONFIG[key]
        if key not in config:
            result[key] = default_val
        elif isinstance(default_val, dict) and isinstance(config[key], dict):
            result[key] = _deep_merge(default_val, config[key])
        else:
            result[key] = config[key]
    return result


class RuleEditorWindow(QMainWindow):
    def __init__(self, initial_path: Path | None = None) -> None:
        super().__init__()
        self._current_path: Path | None = initial_path
        self.setWindowTitle("Rule Editor")
        self.setMinimumSize(560, 620)
        self.resize(660, 700)
        self.setStyleSheet(MILITARY_STYLESHEET)
        self.setFont(QFont("Segoe UI", 9))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_goal_tab(), "Goal rules")
        self._tabs.addTab(self._build_obstacle_tab(), "Obstacle rules")
        self._tabs.addTab(self._build_sectors_tab(), "Sectors")
        self._tabs.addTab(self._build_blending_tab(), "Blending")
        self._tabs.addTab(self._build_output_tab(), "Output")
        layout.addWidget(self._tabs)

        btn_layout = QHBoxLayout()
        self._open_btn = QPushButton("Open")
        self._open_btn.clicked.connect(self._on_open)
        self._open_btn.setToolTip("Load rules JSON file")
        btn_layout.addWidget(self._open_btn)
        self._import_btn = QPushButton("Import")
        self._import_btn.clicked.connect(self._on_import)
        self._import_btn.setToolTip("Import rules and merge with defaults for missing fields")
        btn_layout.addWidget(self._import_btn)
        self._new_btn = QPushButton("New")
        self._new_btn.clicked.connect(self._on_new)
        self._new_btn.setToolTip("Reset to default config")
        btn_layout.addWidget(self._new_btn)
        btn_layout.addStretch()
        self._validate_btn = QPushButton("Validate")
        self._validate_btn.clicked.connect(self._on_validate)
        self._validate_btn.setProperty("primary", "true")
        btn_layout.addWidget(self._validate_btn)
        self._save_btn = QPushButton("Save")
        self._save_btn.clicked.connect(self._on_save)
        self._save_btn.setProperty("primary", "true")
        btn_layout.addWidget(self._save_btn)
        layout.addLayout(btn_layout)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #8b949e; padding: 4px 0;")
        layout.addWidget(self._status)

        if self._current_path and self._current_path.exists():
            self._load_from_path(self._current_path)
            self._status.setText(f"Loaded: {self._current_path}")
        else:
            self._apply_config(DEFAULT_CONFIG)
            self._status.setText("New config (defaults). Use Save to write JSON.")

    def _build_goal_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._goal_classes = QPlainTextEdit()
        self._goal_classes.setPlaceholderText("One per line or comma-separated (e.g. person, red-marker)")
        self._goal_classes.setMaximumHeight(80)
        form.addRow("Goal classes:", self._goal_classes)
        self._priority = QComboBox()
        self._priority.addItems(_PRIORITY_OPTIONS)
        self._priority.setCurrentText("confidence_times_area")
        form.addRow("Priority:", self._priority)
        self._min_confidence = QSlider(Qt.Orientation.Horizontal)
        self._min_confidence.setRange(0, 100)
        self._min_confidence.setValue(50)
        self._min_confidence.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._min_confidence.valueChanged.connect(
            lambda v: self._min_conf_label.setText(f"{v / 100:.2f}")
        )
        self._min_conf_label = QLabel("0.50")
        row = QHBoxLayout()
        row.addWidget(self._min_confidence)
        row.addWidget(self._min_conf_label)
        form.addRow("Min confidence:", row)
        self._min_area_ratio = QSlider(Qt.Orientation.Horizontal)
        self._min_area_ratio.setRange(0, 100)
        self._min_area_ratio.setValue(0)
        self._min_area_label = QLabel("0.00")
        self._min_area_ratio.valueChanged.connect(
            lambda v: self._min_area_label.setText(f"{v / 100:.2f}")
        )
        row2 = QHBoxLayout()
        row2.addWidget(self._min_area_ratio)
        row2.addWidget(self._min_area_label)
        form.addRow("Min area ratio:", row2)
        return w

    def _build_obstacle_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._obstacle_classes = QPlainTextEdit()
        self._obstacle_classes.setPlaceholderText("One per line or comma-separated (e.g. car, truck)")
        self._obstacle_classes.setMaximumHeight(120)
        form.addRow("Obstacle classes:", self._obstacle_classes)
        return w

    def _build_sectors_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._sector_mode = QLineEdit()
        self._sector_mode.setPlaceholderText("thirds")
        form.addRow("Mode:", self._sector_mode)
        self._approach_zone = QSlider(Qt.Orientation.Horizontal)
        self._approach_zone.setRange(1, 100)
        self._approach_zone.setValue(55)
        self._approach_zone_label = QLabel("0.55")
        self._approach_zone.valueChanged.connect(
            lambda v: self._approach_zone_label.setText(f"{v / 100:.2f}")
        )
        row = QHBoxLayout()
        row.addWidget(self._approach_zone)
        row.addWidget(self._approach_zone_label)
        form.addRow("Approach zone height ratio:", row)
        return w

    def _build_blending_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._goal_weight = QSlider(Qt.Orientation.Horizontal)
        self._goal_weight.setRange(0, 100)
        self._goal_weight.setValue(65)
        self._goal_weight_label = QLabel("0.65")
        self._goal_weight.valueChanged.connect(
            lambda v: self._goal_weight_label.setText(f"{v / 100:.2f}")
        )
        row = QHBoxLayout()
        row.addWidget(self._goal_weight)
        row.addWidget(self._goal_weight_label)
        form.addRow("Goal weight:", row)
        bias_layout = QHBoxLayout()
        self._bias_left = QSpinBox()
        self._bias_left.setRange(-180, 180)
        self._bias_left.setValue(-25)
        self._bias_center = QSpinBox()
        self._bias_center.setRange(-180, 180)
        self._bias_center.setValue(0)
        self._bias_right = QSpinBox()
        self._bias_right.setRange(-180, 180)
        self._bias_right.setValue(25)
        bias_layout.addWidget(QLabel("Left:"))
        bias_layout.addWidget(self._bias_left)
        bias_layout.addWidget(QLabel("Center:"))
        bias_layout.addWidget(self._bias_center)
        bias_layout.addWidget(QLabel("Right:"))
        bias_layout.addWidget(self._bias_right)
        form.addRow("Obstacle bias (deg):", bias_layout)
        clamp_layout = QHBoxLayout()
        self._heading_clamp_min = QSpinBox()
        self._heading_clamp_min.setRange(-180, 180)
        self._heading_clamp_min.setValue(-40)
        self._heading_clamp_max = QSpinBox()
        self._heading_clamp_max.setRange(-180, 180)
        self._heading_clamp_max.setValue(40)
        clamp_layout.addWidget(self._heading_clamp_min)
        clamp_layout.addWidget(QLabel("to"))
        clamp_layout.addWidget(self._heading_clamp_max)
        form.addRow("Heading clamp [min, max]:", clamp_layout)
        self._speed_scale_visible = QSlider(Qt.Orientation.Horizontal)
        self._speed_scale_visible.setRange(0, 100)
        self._speed_scale_visible.setValue(85)
        self._speed_scale_visible_label = QLabel("0.85")
        self._speed_scale_visible.valueChanged.connect(
            lambda v: self._speed_scale_visible_label.setText(f"{v / 100:.2f}")
        )
        row_vis = QHBoxLayout()
        row_vis.addWidget(self._speed_scale_visible)
        row_vis.addWidget(self._speed_scale_visible_label)
        form.addRow("Speed scale when goal visible:", row_vis)
        self._reduction_table = QTableWidget(0, 2)
        self._reduction_table.setHorizontalHeaderLabels(["Threshold", "Speed scale"])
        self._reduction_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        red_btn_row = QHBoxLayout()
        add_row_btn = QPushButton("+ Add row")
        add_row_btn.clicked.connect(self._on_add_reduction_row)
        remove_row_btn = QPushButton("− Remove row")
        remove_row_btn.clicked.connect(self._on_remove_reduction_row)
        red_btn_row.addWidget(add_row_btn)
        red_btn_row.addWidget(remove_row_btn)
        red_btn_row.addStretch()
        form.addRow(self._reduction_table)
        form.addRow("", red_btn_row)
        return w

    def _build_output_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        out_min = QHBoxLayout()
        self._out_heading_min = QSpinBox()
        self._out_heading_min.setRange(-180, 180)
        self._out_heading_min.setValue(-40)
        self._out_heading_max = QSpinBox()
        self._out_heading_max.setRange(-180, 180)
        self._out_heading_max.setValue(40)
        out_min.addWidget(self._out_heading_min)
        out_min.addWidget(QLabel("to"))
        out_min.addWidget(self._out_heading_max)
        form.addRow("Heading bounds (deg):", out_min)
        out_speed = QHBoxLayout()
        self._out_speed_min = QLineEdit()
        self._out_speed_min.setPlaceholderText("0.2")
        self._out_speed_max = QLineEdit()
        self._out_speed_max.setPlaceholderText("1.0")
        out_speed.addWidget(self._out_speed_min)
        out_speed.addWidget(QLabel("to"))
        out_speed.addWidget(self._out_speed_max)
        form.addRow("Speed scale bounds:", out_speed)
        return w

    def _collect_config(self) -> dict[str, Any]:
        reduction = []
        for r in range(self._reduction_table.rowCount()):
            th = self._reduction_table.item(r, 0)
            sc = self._reduction_table.item(r, 1)
            if th is not None and sc is not None:
                try:
                    reduction.append({
                        "threshold": float(th.text()),
                        "speed_scale": float(sc.text()),
                    })
                except ValueError:
                    pass
        try:
            out_speed_min = float(self._out_speed_min.text() or "0.2")
        except ValueError:
            out_speed_min = 0.2
        try:
            out_speed_max = float(self._out_speed_max.text() or "1.0")
        except ValueError:
            out_speed_max = 1.0
        return {
            "version": "1.0",
            "goal_rules": {
                "goal_classes": _parse_list_text(self._goal_classes.toPlainText()),
                "priority": self._priority.currentText(),
                "min_confidence": self._min_confidence.value() / 100.0,
                "min_area_ratio": self._min_area_ratio.value() / 100.0,
            },
            "obstacle_rules": {
                "obstacle_classes": _parse_list_text(self._obstacle_classes.toPlainText()),
            },
            "sectors": {
                "mode": self._sector_mode.text().strip() or "thirds",
                "approach_zone_height_ratio": self._approach_zone.value() / 100.0,
            },
            "blending": {
                "goal_weight": self._goal_weight.value() / 100.0,
                "obstacle_bias_deg": {
                    "left": self._bias_left.value(),
                    "center": self._bias_center.value(),
                    "right": self._bias_right.value(),
                },
                "heading_clamp_deg": [self._heading_clamp_min.value(), self._heading_clamp_max.value()],
                "speed_scale_when_goal_visible": self._speed_scale_visible.value() / 100.0,
                "speed_scale_reduction_by_center_score": reduction,
            },
            "output": {
                "heading_bounds_deg": [self._out_heading_min.value(), self._out_heading_max.value()],
                "speed_scale_bounds": [out_speed_min, out_speed_max],
            },
        }

    def _apply_config(self, config: dict[str, Any]) -> None:
        gr = config.get("goal_rules", {})
        self._goal_classes.setPlainText(_format_list(gr.get("goal_classes", [])))
        prio = gr.get("priority", "confidence_times_area")
        idx = self._priority.findText(prio)
        self._priority.setCurrentIndex(idx if idx >= 0 else 0)
        self._min_confidence.setValue(int((gr.get("min_confidence", 0.5) * 100)))
        self._min_area_ratio.setValue(int((gr.get("min_area_ratio", 0) * 100)))
        or_ = config.get("obstacle_rules", {})
        self._obstacle_classes.setPlainText(_format_list(or_.get("obstacle_classes", [])))
        sec = config.get("sectors", {})
        self._sector_mode.setText(sec.get("mode", "thirds"))
        self._approach_zone.setValue(int((sec.get("approach_zone_height_ratio", 0.55) * 100)))
        bl = config.get("blending", {})
        self._goal_weight.setValue(int((bl.get("goal_weight", 0.65) * 100)))
        bias = bl.get("obstacle_bias_deg", {"left": -25, "center": 0, "right": 25})
        self._bias_left.setValue(bias.get("left", -25))
        self._bias_center.setValue(bias.get("center", 0))
        self._bias_right.setValue(bias.get("right", 25))
        clamp = bl.get("heading_clamp_deg", [-40, 40])
        self._heading_clamp_min.setValue(clamp[0] if len(clamp) >= 2 else -40)
        self._heading_clamp_max.setValue(clamp[1] if len(clamp) >= 2 else 40)
        self._speed_scale_visible.setValue(int((bl.get("speed_scale_when_goal_visible", 0.85) * 100)))
        reduction = bl.get("speed_scale_reduction_by_center_score", [])
        self._reduction_table.setRowCount(len(reduction))
        for r, item in enumerate(reduction):
            self._reduction_table.setItem(r, 0, QTableWidgetItem(str(item.get("threshold", 0))))
            self._reduction_table.setItem(r, 1, QTableWidgetItem(str(item.get("speed_scale", 0))))
        out = config.get("output", {})
        hb = out.get("heading_bounds_deg", [-40, 40])
        self._out_heading_min.setValue(hb[0] if len(hb) >= 2 else -40)
        self._out_heading_max.setValue(hb[1] if len(hb) >= 2 else 40)
        sb = out.get("speed_scale_bounds", [0.2, 1.0])
        self._out_speed_min.setText(str(sb[0]) if len(sb) >= 2 else "0.2")
        self._out_speed_max.setText(str(sb[1]) if len(sb) >= 2 else "1.0")

    def _load_from_path(self, path: Path) -> None:
        try:
            config = load_config(path)
            self._apply_config(config)
        except Exception as e:
            QMessageBox.critical(self, "Load error", str(e))

    def _on_open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open rules JSON", "", "JSON (*.json);;All files (*)"
        )
        if path:
            self._current_path = Path(path)
            self._load_from_path(self._current_path)
            self._status.setText(f"Loaded: {path}")

    def _on_import(self) -> None:
        """Import rules from JSON; merge with defaults for any missing fields, then populate form."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Import rules JSON", "", "JSON (*.json);;All files (*)"
        )
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            merged = _merge_with_defaults(data)
            load_config_from_dict(merged)
            self._apply_config(merged)
            self._status.setText(f"Imported: {path} (missing fields filled with defaults)")
        except Exception as e:
            QMessageBox.critical(self, "Import error", str(e))

    def _on_add_reduction_row(self) -> None:
        row = self._reduction_table.rowCount()
        self._reduction_table.insertRow(row)
        self._reduction_table.setItem(row, 0, QTableWidgetItem("0.2"))
        self._reduction_table.setItem(row, 1, QTableWidgetItem("0.5"))

    def _on_remove_reduction_row(self) -> None:
        row = self._reduction_table.currentRow()
        if row >= 0:
            self._reduction_table.removeRow(row)

    def _on_new(self) -> None:
        self._current_path = None
        self._apply_config(DEFAULT_CONFIG)
        self._status.setText("New config (defaults). Save to write JSON.")

    def _on_validate(self) -> None:
        try:
            data = self._collect_config()
            load_config_from_dict(data)
            self._status.setText("Validation OK.")
            QMessageBox.information(self, "Validate", "Config is valid.")
        except Exception as e:
            self._status.setText("Validation failed.")
            QMessageBox.critical(self, "Validation error", str(e))

    def _on_save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save rules JSON",
            str(self._current_path) if self._current_path else "",
            "JSON (*.json);;All files (*)",
        )
        if not path:
            return
        try:
            data = self._collect_config()
            load_config_from_dict(data)
            Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
            self._current_path = Path(path)
            self._status.setText(f"Saved: {path}")
            QMessageBox.information(self, "Saved", f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save error", str(e))


def main() -> None:
    app = QApplication(sys.argv)
    initial_path: Path | None = None
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if p.exists():
            initial_path = p
    win = RuleEditorWindow(initial_path)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
