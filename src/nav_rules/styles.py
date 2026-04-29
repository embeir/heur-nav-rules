"""Military-style QSS theme for nav-rules editor."""
from __future__ import annotations

MILITARY_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0c0e0f;
    color: #d4d7d9;
}

QTabWidget::pane {
    border: 1px solid #2d3238;
    border-radius: 2px;
    background-color: #131619;
    margin-top: 0;
    padding: 10px;
}

QTabBar::tab {
    background-color: #1a1e22;
    color: #9ca3a9;
    padding: 8px 18px;
    margin-right: 2px;
    border: 1px solid #2d3238;
    border-bottom: none;
    border-top-left-radius: 2px;
    border-top-right-radius: 2px;
}

QTabBar::tab:selected {
    background-color: #131619;
    color: #6b8e5a;
    border-bottom: 2px solid #4a7c3e;
}

QTabBar::tab:hover:!selected {
    background-color: #2d3238;
}

QPushButton {
    background-color: #1a1e22;
    color: #d4d7d9;
    border: 1px solid #2d3238;
    border-radius: 2px;
    padding: 7px 14px;
    min-width: 72px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #252b32;
    border-color: #4a7c3e;
}

QPushButton:pressed {
    background-color: #0c0e0f;
    border-color: #6b8e5a;
}

QPushButton:focus {
    border-color: #6b8e5a;
}

QPushButton[primary="true"] {
    background-color: #3d5a3c;
    border-color: #4a7c3e;
    color: #ffffff;
}

QPushButton[primary="true"]:hover {
    background-color: #4a7c3e;
    border-color: #5a9660;
}

QPushButton[primary="true"]:pressed {
    background-color: #2d422c;
}

QLineEdit, QPlainTextEdit, QSpinBox {
    background-color: #0c0e0f;
    color: #d4d7d9;
    border: 1px solid #2d3238;
    border-radius: 2px;
    padding: 6px;
    selection-background-color: #3d5a3c;
}

QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {
    border-color: #4a7c3e;
}

QPlainTextEdit {
    font-family: 'Consolas', 'Monaco', monospace;
}

QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #1a1e22;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #4a7c3e;
    border: 1px solid #2d3238;
    width: 14px;
    margin: -4px 0;
    border-radius: 2px;
}

QSlider::handle:horizontal:hover {
    background: #5a9660;
}

QSlider::sub-page:horizontal {
    background: #3d5a3c;
    border-radius: 3px;
}

QTableWidget {
    background-color: #0c0e0f;
    alternate-background-color: #131619;
    gridline-color: #2d3238;
    border: 1px solid #2d3238;
    border-radius: 2px;
}

QTableWidget::item {
    padding: 5px;
}

QHeaderView::section {
    background-color: #1a1e22;
    color: #9ca3a9;
    padding: 7px;
    border: none;
    border-right: 1px solid #2d3238;
    border-bottom: 1px solid #2d3238;
}

QLabel {
    color: #d4d7d9;
}

QComboBox {
    background-color: #0c0e0f;
    color: #d4d7d9;
    border: 1px solid #2d3238;
    border-radius: 2px;
    padding: 6px 24px 6px 8px;
    min-width: 120px;
}

QComboBox:hover {
    border-color: #4a7c3e;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
    background-color: #1a1e22;
}

QComboBox::down-arrow {
    width: 10px;
    height: 10px;
    border-left: 2px solid #9ca3a9;
    border-bottom: 2px solid #9ca3a9;
    margin-right: 4px;
}

QScrollArea {
    border: none;
}

QScrollBar:vertical {
    background: #0c0e0f;
    width: 12px;
    margin: 0;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #2d3238;
    min-height: 24px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #4a7c3e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""
