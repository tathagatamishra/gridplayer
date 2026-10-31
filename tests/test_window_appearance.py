from unittest.mock import Mock

import pytest

from gridplayer.utils import win32_window


@pytest.mark.parametrize(("square", "preference"), [(True, 1), (False, 0)])
def test_native_corner_preference(mocker, square, preference):
    mocker.patch.object(win32_window, "_is_windows_11", return_value=True)
    mocker.patch.object(win32_window, "_load_dwmapi")
    setter = mocker.patch.object(win32_window, "_dwm_set")
    mocker.patch.object(win32_window, "is_dark_mode", return_value=False)
    widget = Mock()
    widget.winId.return_value = 42
    widget.property.return_value = square
    mocker.patch.object(win32_window, "_colorref", return_value=0)
    win32_window.apply_native_background(widget)
    assert any(call.args[1:] == (33, preference) for call in setter.call_args_list)


def test_native_background_skips_other_platforms(mocker):
    mocker.patch.object(win32_window, "_is_windows_11", return_value=False)
    load = mocker.patch.object(win32_window, "_load_dwmapi")
    win32_window.apply_native_background(Mock())
    load.assert_not_called()
