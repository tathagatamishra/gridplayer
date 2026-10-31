"""Small controls must not shrink native surfaces or clip menu rows."""

import os

from PyQt5.QtCore import QPoint

from gridplayer.params.static import FONT_SIZE_MAIN

SETTINGS = {"player/ui_scale": 50}


def scenario(d):
    d.check("native scale is not overridden", "QT_SCALE_FACTOR" not in os.environ)
    d.check("small UI font", d.app.font().pointSizeF() == FONT_SIZE_MAIN * 0.5)
    d.open(d.media.clips[0])
    block = d.wait_for_cell("a.mp4")
    d.ctx.active_block = block
    # The offscreen clipboard initially has no MIME data.
    d.app.clipboard().setText("")
    menu = d.player._managers_inst["menu"].make_menu()
    menu.popup(QPoint(20, 20))
    d.app.processEvents()
    for action in menu.actions():
        if action.isVisible() and not action.isSeparator():
            rect = menu.actionGeometry(action)
            d.check(
                "menu row fits: " + action.text(),
                rect.height() >= menu.fontMetrics().height(),
            )
    d.shot("small-menu", menu)
    menu.hide()
    menu.deleteLater()
