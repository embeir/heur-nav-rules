import json
from pathlib import Path

from nav_rules.detection import Detection


def test_detection_from_dict_minimal():
    d = {"label": "person", "confidence": 0.9, "center_x": 100, "center_y": 80}
    det = Detection.from_dict(d)
    assert det.label == "person"
    assert det.confidence == 0.9
    assert det.center_x == 100
    assert det.center_y == 80
    assert det.area_ratio == 0.0
    assert det.source == ""


def test_detection_from_dict_full():
    d = {
        "label": "red-marker",
        "confidence": 0.8,
        "center_x": 200,
        "center_y": 120,
        "area_ratio": 0.05,
        "source": "hsv",
    }
    det = Detection.from_dict(d)
    assert det.area_ratio == 0.05
    assert det.source == "hsv"


def test_detection_confidence_clamped():
    det = Detection.from_dict(
        {"label": "x", "confidence": 1.5, "center_x": 0, "center_y": 0}
    )
    assert det.confidence == 1.0


def test_detection_schema_file_exists():
    schema_path = Path(__file__).resolve().parent.parent / "src" / "nav_rules" / "schemas" / "detection_schema.json"
    assert schema_path.exists()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    assert data["required"] == ["label", "confidence", "center_x", "center_y"]
