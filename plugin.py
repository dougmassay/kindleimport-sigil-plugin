# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import os
import sys
import zipfile
from contextlib import contextmanager
from datetime import datetime, timedelta


from kindleunpackcore.compatibility_utils import PY2, unicode_str
from kindleunpackcore.unipath import pathof
from utilities import expanduser, file_open
from updatecheck import UpdateChecker

if PY2:
    from Tkinter import Tk
    import tkFileDialog as tkinter_filedialog
    import tkMessageBox as tkinter_msgbox
else:
    from tkinter import Tk
    import tkinter.filedialog as tkinter_filedialog
    import tkinter.messagebox as tkinter_msgbox

'''
import inspect
SCRIPT_DIR = os.path.normpath(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
print (SCRIPT_DIR)
PLUGIN_NAME = os.path.split(SCRIPT_DIR)[-1]
print (PLUGIN_NAME)
PLUG_DIR = os.path.dirname(SCRIPT_DIR)
print (PLUG_DIR)
'''

_DEBUG_ = False

prefs = {}

@contextmanager
def make_temp_directory():
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def isEPUB(zip):
    if not zipfile.is_zipfile(zip):
        return False
    with zipfile.ZipFile(zip, 'r') as archive:
        mimetype = b'application/epub+zip'
        if PY2:
            mimetype = 'application/epub+zip'
        if archive.infolist()[0].filename != 'mimetype':
            return False
        elif archive.read('mimetype') == mimetype:
            return True
        else:
            return False

def fileChooser():
    localRoot = Tk()
    localRoot.withdraw()
    file_opt = {}
    file_opt['parent'] = None
    file_opt['title']= 'Select Kindlebook file'
    file_opt['defaultextension'] = '.azw3'
    # retrieve the initialdir from JSON prefs
    file_opt['initialdir'] = unicode_str(prefs['use_file_path'], 'utf-8')
    file_opt['multiple'] = False
    file_opt['filetypes'] = [('Kindlebooks', ('.azw', '.azw3', '.prc', '.mobi'))]
    localRoot.quit()
    return tkinter_filedialog.askopenfilename(**file_opt)

def update_msgbox(title, msg):
    localRoot = Tk()
    localRoot.withdraw()
    localRoot.option_add('*font', 'Helvetica -12')
    localRoot.quit()
    return tkinter_msgbox.showinfo(title, msg)

def run(bk):
    global prefs
    prefs = bk.getPrefs()

    # set default preference values
    if 'use_file_path' not in prefs:
        prefs['use_file_path'] = expanduser('~')
    if 'azw3_epub_version' not in prefs:
        prefs['azw3_epub_version'] = "2"  # A, F, 2 or 3
    if 'use_hd_images' not in prefs:
        prefs['use_hd_images'] = True
    if 'use_src_from_dual_mobi' not in prefs:
        prefs['use_src_from_dual_mobi'] = True

    if 'last_time_checked' not in prefs:
        prefs['last_time_checked'] = str(datetime.now() - timedelta(hours=7))
    if 'last_online_version' not in prefs:
        prefs['last_online_version'] = '0.1.0'

    chk = UpdateChecker(prefs['last_time_checked'], prefs['last_online_version'], bk._w)
    update_available, online_version, time = chk.update_info()
    # update preferences with latest date/time/version
    prefs['last_time_checked'] = time
    if online_version is not None:
        prefs['last_online_version'] = online_version
    if update_available:
        title = 'Plugin Update Available'
        msg = 'Version {} of the {} plugin is now available.'.format(online_version, bk._w.plugin_name)
        update_msgbox(title, msg)

    if _DEBUG_:
        print('Python sys.path', sys.path)
        print('Default AZW3 epub version:', prefs['azw3_epub_version'])

    inpath = fileChooser()
    if inpath == '' or not os.path.exists(inpath):
        print('No input file selected!')
        bk.savePrefs(prefs)
        return 0

    print ('Path to Kindlebook {0}'.format(inpath))
    from mobi_stuff import mobiProcessor, topaz
    if topaz(inpath):
        print('Kindlebook is in Topaz format: can\'t open!')
        bk.savePrefs(prefs)
        return -1

    mobionly = False
    mp = mobiProcessor(inpath, prefs['azw3_epub_version'],  prefs['use_hd_images'])
    # Save last directory accessed to JSON prefs
    prefs['use_file_path'] = pathof(os.path.dirname(inpath))
    if mp.isEncrypted:
        print('Kindlebook is encrypted: can\'t open!')
        bk.savePrefs(prefs)
        return -1
    if mp.isPrintReplica:
        print('Kindlebook is a Print Replica: can\'t open!')
        bk.savePrefs(prefs)
        return -1
    if not mp.isComboFile and not mp.isKF8:
        mobionly = True

    with make_temp_directory() as temp_dir:
        if not mobionly:
            epub, src = mp.unpackEPUB(temp_dir)
            if src is not None and isEPUB(src) and prefs['use_src_from_dual_mobi']:
                print ('Using included kindlegen sources.')
                epub = src
        else:
            from quickepub import QuickEpub
            mobidir, mobi_html, mobi_opf, mobiBaseName = mp.unpackMOBI(temp_dir)
            qe = QuickEpub(mobidir, mobi_html, mobi_opf)
            epub = qe.makeEPUB()

        # Save prefs to json
        bk.savePrefs(prefs)
        print ('Path to epub or src {0}'.format(epub))
        with file_open(epub,'rb')as fp:
            data = fp.read()
        bk.addotherfile('dummy.epub', data)

    return 0

def main():
    print ('I reached main when I should not have\n')
    return -1

if __name__ == "__main__":
    sys.exit(main())
