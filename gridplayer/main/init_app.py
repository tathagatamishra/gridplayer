import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from gridplayer.main.init_icons import init_icon
from gridplayer.main.init_resources import init_resources
from gridplayer.main.init_translator import init_translator
from gridplayer.params import env
from gridplayer.params.static import FONT_SIZE_MAIN
from gridplayer.params.theme import (
    apply_theme,
    create_fusion_style,
    on_system_theme_changed,
)
from gridplayer.settings import Settings
from gridplayer.utils.darkmode import watch_system_theme
from gridplayer.utils.wayland import follow_desktop_cursor


def init_app():
    if env.QT_PLATFORM:
        app = QApplication([*sys.argv, "-platform", env.QT_PLATFORM])
    else:
        app = QApplication(sys.argv)

    scale = max(50, min(200, Settings().get("player/ui_scale"))) / 100
    app.setProperty("gridplayer_ui_scale", scale)

    follow_desktop_cursor()

    init_resources()

    app.setStyle(create_fusion_style())

    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    app.styleHints().setShowShortcutsInContextMenus(True)

    apply_theme(app)
    app.paletteChanged.connect(lambda: on_system_theme_changed(app))
    watch_system_theme(lambda: on_system_theme_changed(app), app)

    init_icon(app)

    font = QFont("Hack")
    font.setPointSizeF(FONT_SIZE_MAIN * scale)
    app.setFont(font)

    init_translator(app)

    return app
