"""Auto-hide the Windows caption while keeping the native resizing frame."""

from time import monotonic

from PyQt5.QtCore import QObject, Qt, QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication

from gridplayer.settings import Settings
from gridplayer.utils.win32_window import set_caption_visible


class AutoTitleBar(QObject):
    def __init__(self, window):
        super().__init__(window)
        self._visible = True
        self._last_activity = monotonic()
        self._last_position = None
        self._enabled = False
        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self.update_caption)
        self._timer.start()

    def update_caption(self):
        window = self.parent()
        now = monotonic()
        enabled = Settings().get("player/hide_title_bar")
        if enabled != self._enabled:
            self._enabled = enabled
            self._last_activity = now
        if not window.isVisible() or window.isMinimized() or window.isFullScreen():
            self._last_activity = now
            return
        if not enabled:
            if not self._visible:
                self._set_visible(True)
            return

        self._set_visible(self._visible)
        position = QCursor.pos()
        frame = window.frameGeometry()
        inside = frame.contains(position)
        # Keep the caption available while its buttons or drag area are in use.
        caption_bottom = window.mapToGlobal(window.rect().topLeft()).y()
        on_caption = inside and position.y() < caption_bottom
        at_top = inside and position.y() < frame.top() + 8
        busy = (
            QApplication.mouseButtons() != Qt.NoButton
            or QApplication.activePopupWidget() is not None
            or QApplication.activeModalWidget() is not None
        )
        moved = position != self._last_position
        self._last_position = position
        if busy or on_caption or (self._visible and inside and moved):
            self._last_activity = now
        if not self._visible and at_top and not busy:
            self._set_visible(True)
            self._last_activity = now
        elif self._visible and not busy and not on_caption:
            timeout = max(1, min(60, Settings().get("player/title_bar_timeout")))
            if now - self._last_activity >= timeout:
                self._set_visible(False)

    def _set_visible(self, visible):
        # Query/apply the native style even when our state is unchanged: Qt can
        # restore frame styles on leaving fullscreen or changing window flags.
        if set_caption_visible(self.parent(), visible):
            self._visible = visible
