"""Detection dataclass and validation against detection_schema."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Detection:
    """Single detection from any model. Required: label, confidence, center_x, center_y."""

    label: str
    confidence: float
    center_x: float
    center_y: float
    area_ratio: float = 0.0
    source: str = ""

    def __post_init__(self) -> None:
        self.confidence = max(0.0, min(1.0, float(self.confidence)))
        self.area_ratio = max(0.0, min(1.0, float(self.area_ratio)))

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Detection:
        return cls(
            label=str(d["label"]),
            confidence=float(d["confidence"]),
            center_x=float(d["center_x"]),
            center_y=float(d["center_y"]),
            area_ratio=float(d.get("area_ratio", 0.0)),
            source=str(d.get("source", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "confidence": self.confidence,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "area_ratio": self.area_ratio,
            "source": self.source or None,
        }
