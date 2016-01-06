#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os
import sys
import re
import glob
import shutil
import inspect
import zipfile


SCRIPT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
KU_DIR = os.path.join(SCRIPT_DIR, 'kindleunpackcore')
TEMP_DIR = os.path.join(SCRIPT_DIR, 'KindleImport')

PLUGIN_FILES = ['mobiml2xhtml.py',
            'mobi_stuff.py',
            'plugin.py',
            'plugin.xml',
            'quickepub.py',
            'utilities.py']

def findVersion():
    _version_pattern = re.compile(r'<version>([^<]*)</version>')
    with open('plugin.xml', 'r') as fd:
        data = fd.read()
    match = re.search(_version_pattern, data)
    if match is not None:
        return '{}'.format(match.group(1))
    return '0.X.X'

# Find version info from plugin.xml and build zip file name from it
VERS_INFO =  findVersion()
PLUGIN_NAME = os.path.join(SCRIPT_DIR, 'KindleImport_v{}.zip'.format(VERS_INFO))


# recursive zip creation support routine
def zipUpDir(myzip, tdir, localname):
    currentdir = tdir
    if localname != "":
        currentdir = os.path.join(currentdir,localname)
    dir_contents = os.listdir(currentdir)
    for entry in dir_contents:
        afilename = entry
        localfilePath = os.path.join(localname, afilename)
        realfilePath = os.path.join(currentdir, entry)
        if os.path.isfile(realfilePath):
            myzip.write(realfilePath, localfilePath, zipfile.ZIP_DEFLATED)
        elif os.path.isdir(realfilePath):
            zipUpDir(myzip, tdir, localfilePath)

def removePreviousKI(rmzip=False):
    # Remove temp KindleImport folder and contents if it exists
    if os.path.exists(TEMP_DIR) and os.path.isdir(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    if rmzip:
        print ('Removing any leftover zip files ...')
        for each in glob.glob('KindleImport_v*.zip'):
            path = os.path.join(SCRIPT_DIR, each)
            if os.path.exists(path):
                os.remove(path)

def ignore_in_dirs(base, items, ignored_dirs=None):
    ans = []
    if ignored_dirs is None:
        ignored_dirs = {'.git', '__pycache__'}
    for name in items:
        path = os.path.join(base, name)
        if os.path.isdir(path):
            if name in ignored_dirs:
                ans.append(name)
        else:
            if name.rpartition('.')[-1] not in ('py'):
                ans.append(name)
    return ans

if __name__ == "__main__":
    print('Removing any previous build leftovers ...')
    removePreviousKI(rmzip=True)

    # Copy everything to temp directory
    print ('Copying \'kindleunpackcore\' directory to temporary \'KindleImport\' ...')
    try:
        shutil.copytree(KU_DIR, os.path.join(TEMP_DIR, os.path.basename(KU_DIR)), ignore=ignore_in_dirs)
    except:
        sys.exit('Couldn\'t copy necessary kindleunpackcore directory!')
    files = os.listdir(SCRIPT_DIR)

    print ('Copying plugin files to temporary \'KindleImport\' ...')
    try:
        for entry in PLUGIN_FILES:
            shutil.copy2(os.path.join(SCRIPT_DIR, entry), os.path.join(TEMP_DIR, entry))
    except:
        sys.exit('Couldn\'t copy necessary plugin files!')

    print ('Creating {} ...'.format(os.path.basename(PLUGIN_NAME)))
    outzip = zipfile.ZipFile(PLUGIN_NAME, 'w')
    zipUpDir(outzip, SCRIPT_DIR, os.path.basename(TEMP_DIR))
    outzip.close()

    print ('Plugin successfully created!')

    print('Removing temp build directory ...')
    removePreviousKI()
