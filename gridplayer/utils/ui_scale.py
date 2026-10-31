"""Control sizes in logical pixels, independent of native display scaling."""

from PyQt5.QtWidgets import QApplication


def ui_scale() -> float:
    app = QApplication.instance()
    value = app.property("gridplayer_ui_scale") if app else None
    return float(value) if value is not None else 1.0


def scaled_size(value: int) -> int:
    return max(1, round(value * ui_scale()))
