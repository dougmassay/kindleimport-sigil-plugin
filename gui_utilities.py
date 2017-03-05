# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import sys

from compatibility_utils import PY2
from compatibility_utils import unicode_str


def fileChooser(startfolder, gui='tkinter'):
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
        w = QWidget()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(w,'Select Kindlebook file', unicode_str(startfolder, 'utf-8'),
                                                  'Kindlebooks (*.azw *.azw3 *.prc *.mobi)', options=options)
        return fileName

def update_msgbox(title, msg, gui='tkinter'):
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
        w = QWidget()
        return QMessageBox.information(w, title, msg)
