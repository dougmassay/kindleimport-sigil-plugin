# -*- coding: utf-8 -*-
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import unicode_literals, division, absolute_import, print_function

import sys
import os
import re

from compatibility_utils import PY2

if PY2:
    import codecs
    file_open = codecs.open
else:
    file_open = open

if PY2 and sys.platform.startswith("win"):
    import ctypes
    from ctypes import windll, wintypes

    class GUID(ctypes.Structure):
        _fields_ = [
            ('Data1', wintypes.DWORD),
            ('Data2', wintypes.WORD),
            ('Data3', wintypes.WORD),
            ('Data4', wintypes.BYTE * 8)
        ]

        def __init__(self, l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8):
            """Create a new GUID."""
            self.Data1 = l
            self.Data2 = w1
            self.Data3 = w2
            self.Data4[:] = (b1, b2, b3, b4, b5, b6, b7, b8)

        def __repr__(self):
            b1, b2, b3, b4, b5, b6, b7, b8 = self.Data4
            return 'GUID(%x-%x-%x-%x%x%x%x%x%x%x%x)' % (
                       self.Data1, self.Data2, self.Data3, b1, b2, b3, b4, b5, b6, b7, b8)

    # constants to be used according to the version on shell32
    CSIDL_PROFILE = 40
    FOLDERID_Profile = GUID(0x5E6C858F, 0x0E22, 0x4760, 0x9A, 0xFE, 0xEA, 0x33, 0x17, 0xB6, 0x71, 0x73)

    def expanduser(path='~'):
        # get the function that we can find from Vista up, not the one in XP
        get_folder_path = getattr(windll.shell32, 'SHGetKnownFolderPath', None)
        if get_folder_path is not None:
            # ok, we can use the new function which is recomended by the msdn
            ptr = ctypes.c_wchar_p()
            get_folder_path(ctypes.byref(FOLDERID_Profile), 0, 0, ctypes.byref(ptr))
            return ptr.value
        else:
            # use the deprecated one found in XP and on for compatibility reasons
            get_folder_path = getattr(windll.shell32, 'SHGetSpecialFolderPathW', None)
            buf = ctypes.create_unicode_buffer(300)
            get_folder_path(None, buf, CSIDL_PROFILE, False)
            return buf.value
else:
    expanduser = os.path.expanduser

def find_output_encoding(opffile):
    with file_open(opffile, 'r', encoding='utf-8') as fp:
        ml = fp.read()
        match = re.search(r'''<meta\s+name="output encoding"\s+content="([^>]*)"\s?/>''', ml)
        if match.group(1) is not None:
            return match.group(1)
        match = re.search(r'''<meta\s+content="([^>]*)"\s+name="output encoding"\s?/>''', ml)
        if match.group(1) is not None:
            return match.group(1)
        return None

def tweak_opf(opffile, asin, preserve_comments=False):
    dc = None
    if asin is not None:
        dc = '''<dc:identifier opf:scheme="AMAZON">%s</dc:identifier>''' % asin
    with file_open(opffile, 'r', encoding='utf-8') as fp:
        newopf = ''
        for line in fp:
            if dc is not None:
                if line.rstrip().endswith('</dc:language>'):
                    line = line + '\n' + dc
            if preserve_comments:
                line = line.replace('<!-- BEGIN INFORMATION ONLY', '')
                line = line.replace('END INFORMATION ONLY -->', '')
            newopf += line
    try:
        file_open(opffile,'wb').write(newopf.encode('utf-8'))
    except:
        return False
    return True

def get_asin(opffile):
    _meta_pattern = re.compile('<meta name="ASIN" content="([^>]+)"')
    try:
        with file_open(opffile, 'r', encoding='utf-8') as fp:
            opfData = fp.read()
    except:
        return None
    m = _meta_pattern.search(opfData)
    if m:
        asin = m.group(1)
    else:
        return None
    return asin
