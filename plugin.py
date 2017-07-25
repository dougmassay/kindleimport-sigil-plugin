# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import os
import sys
import zipfile
from contextlib import contextmanager
from datetime import datetime, timedelta


from compatibility_utils import PY2, unicode_str
from unipath import pathof
from epub_utils import epub_zip_up_book_contents

from utilities import expanduser, file_open, tweak_opf, get_asin
from gui_utilities import fileChooser, update_msgbox
from updatecheck import UpdateChecker


_DEBUG_ = False

prefs = {}

GUI = None

@contextmanager
def temp_epub_handle(prefix='KindleImport', suffix='.epub', delete=True):
    import tempfile
    fd, temp_file = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    try:
        yield temp_file
    finally:
        if delete:
            os.close(fd)
            os.remove(temp_file)

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


def run(bk):
    global prefs
    global GUI

    if bk.launcher_version() >= 20170115:
        GUI = 'pyqt'
    else:
        GUI = 'tkinter'

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
    if 'asin_for_kindlegen_plugin' not in prefs:
        prefs['asin_for_kindlegen_plugin'] = False
    if 'preserve_kindleunpack_meta' not in prefs:
        prefs['preserve_kindleunpack_meta'] = False

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
        # update_msgbox(title, msg)
        update_msgbox(title, msg, GUI)

    if _DEBUG_:
        print('Python sys.path', sys.path)
        print('Default AZW3 epub version:', prefs['azw3_epub_version'])

    # inpath = fileChooser()
    inpath = fileChooser(prefs['use_file_path'], GUI)
    if inpath == '' or not os.path.exists(inpath):
        print('No input file selected!')
        bk.savePrefs(prefs)
        return 0

    print('Path to Kindlebook {0}'.format(inpath))
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
        TWEAK = True
        asin = None
        if not mobionly:
            epub, opf, src = mp.unpackEPUB(temp_dir)
            if src is not None and isEPUB(src) and prefs['use_src_from_dual_mobi']:
                print('Using included kindlegen sources.')
                epub = src
            else:
                # If user requested no tweaks through preferences, use standard epub from KindleUnpack
                if not prefs['asin_for_kindlegen_plugin'] and not prefs['preserve_kindleunpack_meta']:
                    TWEAK = False
                elif prefs['asin_for_kindlegen_plugin']:
                    if opf is not None:
                        # Get asin from metadata and put it in a dc:meta that the Kindlegen plugin can use.
                        asin = get_asin(opf)
                        if asin is not None:
                            asin = unicode_str(asin)
                    else:
                        TWEAK = False
                if TWEAK:
                    # Modify the opf with the requested tweaks and build a new epub
                    if tweak_opf(opf, asin, epub_version=prefs['azw3_epub_version'], preserve_comments=prefs['preserve_kindleunpack_meta']):
                        os.remove(epub)
                        with temp_epub_handle(delete=False) as new_epub:
                            epub_zip_up_book_contents(os.path.join(temp_dir,'mobi8'), new_epub)
                        epub = new_epub
        else:
            from quickepub import QuickEpub
            mobidir, mobi_html, mobi_opf, mobiBaseName = mp.unpackMOBI(temp_dir)
            if not prefs['asin_for_kindlegen_plugin'] and not prefs['preserve_kindleunpack_meta']:
                TWEAK = False
            elif prefs['asin_for_kindlegen_plugin']:
                if mobi_opf is not None:
                    # Get asin from metadata and put it in a dc:meta that the Kindlegen plugin can use.
                    asin = get_asin(mobi_opf)
                    if asin is not None:
                        asin = unicode_str(asin)
                    else:
                        TWEAK = False
            if TWEAK:
                if not tweak_opf(mobi_opf, asin, preserve_comments=prefs['preserve_kindleunpack_meta']):
                    print('OPF manipulation failed!')
                    return -1
            qe = QuickEpub(mobidir, mobi_html, mobi_opf)
            epub = qe.makeEPUB()

        # Save prefs to json
        bk.savePrefs(prefs)
        print('Path to epub or src {0}'.format(epub))
        with file_open(epub,'rb')as fp:
            data = fp.read()
        bk.addotherfile('dummy.epub', data)

    return 0

def main():
    print('I reached main when I should not have\n')
    return -1


if __name__ == "__main__":
    sys.exit(main())
