# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import os
import struct

from compatibility_utils import PY2, bstr

import kindleunpackcore.kindleunpack as _mu


if PY2:
    range = xrange

def topaz(f):
    with open(f,'rb') as kindle_file:
        return (kindle_file.read(3) == b'TPZ')

class SectionizerLight:
    """ Stolen from Mobi_Unpack and slightly modified. """
    def __init__(self, filename):
        self.data = open(filename, 'rb').read()
        if self.data[:3] == b'TPZ':
            self.ident = 'TPZ'
        else:
            self.palmheader = self.data[:78]
            self.ident = self.palmheader[0x3C:0x3C+8]
        try:
            self.num_sections, = struct.unpack_from(b'>H', self.palmheader, 76)
        except:
            return
        self.filelength = len(self.data)
        try:
            sectionsdata = struct.unpack_from(bstr('>%dL' % (self.num_sections*2)), self.data, 78) + (self.filelength, 0)
            self.sectionoffsets = sectionsdata[::2]
        except:
            pass

    def loadSection(self, section):
        before, after = self.sectionoffsets[section:section+2]
        return self.data[before:after]

class MobiHeaderLight:
    """ Stolen from Mobi_Unpack and slightly modified. """
    def __init__(self, sect, sectNumber):
        self.sect = sect
        self.start = sectNumber
        self.header = self.sect.loadSection(self.start)
        self.records, = struct.unpack_from(b'>H', self.header, 0x8)
        self.length, self.type, self.codepage, self.unique_id, self.version = struct.unpack(b'>LLLLL', self.header[20:40])
        self.mlstart = self.sect.loadSection(self.start+1)[0:4]
        self.crypto_type, = struct.unpack_from(b'>H', self.header, 0xC)

    def isEncrypted(self):
        return self.crypto_type != 0

    def isPrintReplica(self):
        return self.mlstart[0:4] == b'%MOP'

    # Standalone KF8 file
    def isKF8(self):
        return self.start != 0 or self.version == 8

    def isJointFile(self):
        # Check for joint MOBI/KF8
        for i in range(len(self.sect.sectionoffsets)-1):
            before, after = self.sect.sectionoffsets[i:i+2]
            if (after - before) == 8:
                data = self.sect.loadSection(i)
                if data == b'BOUNDARY':
                    return True
                    break
        return False

class mobiProcessor:
    def __init__(self, infile, ePubVersion='2', useHDImages=True):
        self.infile = infile
        self.sect = SectionizerLight(self.infile)
        if (self.sect.ident != b'BOOKMOBI' and self.sect.ident != b'TEXtREAd') or self.sect.ident == 'TPZ':
            raise Exception(_('Unrecognized Kindle/MOBI file format!'))
        mhl = MobiHeaderLight(self.sect, 0)
        self.version = mhl.version
        self.isEncrypted = mhl.isEncrypted()
        if self.sect.ident == b'TEXtREAd':
            self.isPrintReplica = False
            self.isComboFile = False
            self.isKF8 = False
            return
        self.isPrintReplica = mhl.isPrintReplica()
        self.isKF8 = mhl.isKF8()
        self.isComboFile = mhl.isJointFile()
        self.ePubVersion = ePubVersion
        self.useHDImages = useHDImages

    def unpackMOBI(self, outdir):
        _mu.unpackBook(self.infile, outdir, epubver=self.ePubVersion, use_hd=self.useHDImages)
        mobidir = os.path.join(outdir, 'mobi7')
        mobiBaseName = os.path.splitext(os.path.basename(self.infile))[0]
        mobi_opf = os.path.join(mobidir, 'content.opf')
        mobi_html = os.path.join(mobidir, 'book.html')
        if not os.path.exists(mobi_html):
            raise Exception(_('Problem locating unpacked html: {0}'.format(mobi_html)))
        if not os.path.exists(mobi_opf):
            raise Exception(_('Problem locating unpacked opf: {0}'.format(mobi_opf)))
        return (mobidir, mobi_html, mobi_opf, mobiBaseName)

    def unpackEPUB(self, outdir):
        src = None
        _mu.unpackBook(self.infile, outdir, epubver=self.ePubVersion, use_hd=self.useHDImages)
        if os.path.exists(os.path.join(outdir, 'kindlegensrc.zip')):
            src = os.path.join(outdir, 'kindlegensrc.zip')
        kf8dir = os.path.join(outdir, 'mobi8')
        kf8BaseName = os.path.splitext(os.path.basename(self.infile))[0]
        opf = os.path.join(kf8dir, 'OEBPS', 'content.opf')
        if not os.path.exists(opf):
            opf = None
        epub = os.path.join(kf8dir, '{0}.epub'.format(kf8BaseName))
        if not os.path.exists(epub):
            raise Exception(_('Problem locating unpacked epub: {0}'.format(epub)))
        return (epub, opf, src)
