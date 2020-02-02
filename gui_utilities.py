# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import sys

from compatibility_utils import PY2
from compatibility_utils import unicode_str

def dark_palette(bk, app):
    supports_theming = (bk.launcher_version() >= 20200117)
    if not supports_theming:
        return
    if bk.colorMode() != "dark":
        return
    try:
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor, QPalette
        from PyQt5.QtWidgets import QStyleFactory
    except ImportError:
        return

    p = QPalette()
    sigil_colors = bk.color
    dark_color = QColor(sigil_colors("Window"))
    disabled_color = QColor(127,127,127)
    dark_link_color = QColor(108, 180, 238)
    text_color = QColor(sigil_colors("Text"))
    p.setColor(p.Window, dark_color)
    p.setColor(p.WindowText, text_color)
    p.setColor(p.Base, QColor(sigil_colors("Base")))
    p.setColor(p.AlternateBase, dark_color)
    p.setColor(p.ToolTipBase, dark_color)
    p.setColor(p.ToolTipText, text_color)
    p.setColor(p.Text, text_color)
    p.setColor(p.Disabled, p.Text, disabled_color)
    p.setColor(p.Button, dark_color)
    p.setColor(p.ButtonText, text_color)
    p.setColor(p.Disabled, p.ButtonText, disabled_color)
    p.setColor(p.BrightText, Qt.red)
    p.setColor(p.Link, dark_link_color)
    p.setColor(p.Highlight, QColor(sigil_colors("Highlight")))
    p.setColor(p.HighlightedText, QColor(sigil_colors("HighlightedText")))
    p.setColor(p.Disabled, p.HighlightedText, disabled_color)

    app.setStyle(QStyleFactory.create("Fusion"))
    app.setPalette(p)

def fileChooser(startfolder, bk, gui='tkinter'):
    if gui == 'tkinter':
        if PY2:
            from Tkinter import Tk
            import tkFileDialog as tkinter_filedialog
            # import tkMessageBox as tkinter_msgbox
        else:
            from tkinter import Tk
            import tkinter.filedialog as tkinter_filedialog
            # import tkinter.messagebox as tkinter_msgbox

        localRoot = Tk()
        localRoot.withdraw()
        file_opt = {}
        file_opt['parent'] = None
        file_opt['title']= 'Select Kindlebook file'
        file_opt['defaultextension'] = '.azw3'
        # retrieve the initialdir from JSON prefs
        file_opt['initialdir'] = unicode_str(startfolder, 'utf-8')
        file_opt['multiple'] = False
        file_opt['filetypes'] = [('Kindlebooks', ('.azw', '.azw3', '.prc', '.mobi'))]
        localRoot.quit()
        return tkinter_filedialog.askopenfilename(**file_opt)
    elif gui == 'pyqt':
        from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog

        app = QApplication(sys.argv)
        dark_palette(bk, app)
        w = QWidget()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(w,'Select Kindlebook file', unicode_str(startfolder, 'utf-8'),
                                                  'Kindlebooks (*.azw *.azw3 *.prc *.mobi)', options=options)
        return fileName

def update_msgbox(title, msg, bk, gui='tkinter'):
    if gui == 'tkinter':
        if PY2:
            from Tkinter import Tk
            import tkMessageBox as tkinter_msgbox
        else:
            from tkinter import Tk
            import tkinter.messagebox as tkinter_msgbox
        localRoot = Tk()
        localRoot.withdraw()
        localRoot.option_add('*font', 'Helvetica -12')
        localRoot.quit()
        return tkinter_msgbox.showinfo(title, msg)
    elif gui == 'pyqt':
        from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox

        app = QApplication(sys.argv)
        dark_palette(bk, app)
        w = QWidget()
        return QMessageBox.information(w, title, msg)
