from types import SimpleNamespace

import pytest
from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtWidgets import QApplication, QWidget

from gridplayer.widgets import auto_title_bar as module


@pytest.fixture
def caption(mocker):
    app = QApplication.instance() or QApplication([])
    window = QWidget()
    window.resize(800, 450)
    window.show()
    values = {"player/hide_title_bar": True, "player/title_bar_timeout": 3}
    mocker.patch.object(
        module, "Settings", return_value=SimpleNamespace(get=values.get)
    )
    clock = mocker.patch.object(module, "monotonic", return_value=0)
    cursor = mocker.patch.object(module.QCursor, "pos", return_value=QPoint(400, 200))
    mocker.patch.object(window, "frameGeometry", return_value=QRect(0, 0, 800, 480))
    mocker.patch.object(window, "mapToGlobal", return_value=QPoint(0, 30))
    apply = mocker.patch.object(module, "set_caption_visible", return_value=True)
    mocker.patch.object(module.QApplication, "mouseButtons", return_value=Qt.NoButton)
    mocker.patch.object(module.QApplication, "activePopupWidget", return_value=None)
    mocker.patch.object(module.QApplication, "activeModalWidget", return_value=None)
    control = module.AutoTitleBar(window)
    control._timer.stop()
    control.update_caption()
    yield SimpleNamespace(
        control=control,
        clock=clock,
        cursor=cursor,
        window=window,
        values=values,
        apply=apply,
        app=app,
    )
    window.hide()
    window.deleteLater()


def test_custom_delay_and_top_edge_reveal(caption):
    c = caption
    c.values["player/title_bar_timeout"] = 5
    c.clock.return_value = 4
    c.control.update_caption()
    assert c.control._visible
    c.clock.return_value = 5
    c.control.update_caption()
    assert not c.control._visible
    c.cursor.return_value = QPoint(300, 4)
    c.control.update_caption()
    assert c.control._visible


@pytest.mark.parametrize(
    "busy", ["mouseButtons", "activePopupWidget", "activeModalWidget"]
)
def test_does_not_hide_during_interaction(caption, mocker, busy):
    mocker.patch.object(
        module.QApplication,
        busy,
        return_value=Qt.LeftButton if busy == "mouseButtons" else caption.window,
    )
    caption.clock.return_value = 10
    caption.control.update_caption()
    assert caption.control._visible


def test_disabling_restores_caption_immediately(caption):
    caption.clock.return_value = 4
    caption.control.update_caption()
    assert not caption.control._visible
    caption.values["player/hide_title_bar"] = False
    caption.control.update_caption()
    assert caption.control._visible


def test_fullscreen_is_left_alone(caption, mocker):
    mocker.patch.object(caption.window, "isFullScreen", return_value=True)
    caption.apply.reset_mock()
    caption.clock.return_value = 20
    caption.control.update_caption()
    caption.apply.assert_not_called()
