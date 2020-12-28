# -*- coding: utf-8 -*-
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import unicode_literals, division, absolute_import, print_function

import os
import zipfile
from utilities import file_open, find_output_encoding
from kindleunpackcore.compatibility_utils import unicode_str
from mobiml2xhtml import MobiMLConverter
import sigil_gumbo_bs4_adapter as gumbo_bs4

has_cssutils = True
try:
    import cssutils
except ImportError:
    has_cssutils = False

class ZipInfo(zipfile.ZipInfo):
    def __init__(self, *args, **kwargs):
        if 'compress_type' in kwargs:
            compress_type = kwargs.pop('compress_type')
        super(ZipInfo, self).__init__(*args, **kwargs)
        self.compress_type = compress_type

class QuickEpub(object):
    def __init__(self, outdir, htmlfile, opffile):
        self.outdir, self.htmlfile, self.opffile = outdir, htmlfile, opffile
        self.epubname = os.path.join(outdir,'new.epub')
        self.metainf = os.path.join(outdir,'META-INF')
        if not os.path.exists(self.metainf):
            os.mkdir(self.metainf)

        container = '<?xml version="1.0" encoding="UTF-8"?>\n'
        container += '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        container += '    <rootfiles>\n'
        container += '<rootfile full-path="{0}" media-type="application/oebps-package+xml"/>'.format(os.path.basename(self.opffile))
        container += '    </rootfiles>\n</container>\n'
        fileout = os.path.join(self.metainf,'container.xml')
        file_open(fileout,'wb').write(container.encode('utf-8'))

    def removeThumbnailImage(self, img_dir):
        if not os.path.isdir(img_dir):
            return
        img_list = os.listdir(img_dir)
        for img_file in img_list:
            if img_file.startswith('thumb'):
                os.remove(os.path.join(img_dir, img_file))
                break

    # recursive zip creation support routine
    def zipUpDir(self, myzip, tdir, localname):
        currentdir = tdir
        if localname != "":
            currentdir = os.path.join(currentdir,localname)
        list = os.listdir(currentdir)
        for file in list:
            afilename = file
            localfilePath = os.path.join(localname, afilename)
            realfilePath = os.path.join(currentdir,file)
            if os.path.isfile(realfilePath):
                myzip.write(realfilePath, localfilePath, zipfile.ZIP_DEFLATED)
            elif os.path.isdir(realfilePath):
                self.zipUpDir(myzip, tdir, localfilePath)

    def makeEPUB(self):
        out_enc = find_output_encoding(self.opffile)
        print('Markup encoded as:', out_enc)
        ml2html = MobiMLConverter(self.htmlfile, out_enc)
        xhtmlstr, css, cssname = ml2html.processml()
        soup = gumbo_bs4.parse(xhtmlstr)
        xhtmlstr = soup.prettyprint_xhtml()
        file_open(self.htmlfile,'wb').write(xhtmlstr.encode('utf-8'))
        if has_cssutils:
            sheet = cssutils.parseString(css)
            cssutils.ser.prefs.indent = 2*' '
            cssutils.ser.prefs.indentClosingBrace = False
            cssutils.ser.prefs.omitLastSemicolon = False
            css = unicode_str(sheet.cssText)
        file_open(cssname,'wb').write(css.encode('utf-8'))

        with file_open(self.opffile, 'r', encoding='utf-8') as fp:
            newopf = ''
            for line in fp:
                if line.startswith('<item'):
                    if line.find('text/x-oeb1-document'):
                        line = line.replace('text/x-oeb1-document', 'application/xhtml+xml')
                    if line.find('text/html'):
                        line = line.replace('text/html', 'application/xhtml+xml')
                newopf += line
                if line.startswith('<manifest>'):
                    newopf += '<item id="css_file" media-type="text/css" href="styles.css" />\n'

        file_open(self.opffile,'wb').write(newopf.encode('utf-8'))

        outzip = zipfile.ZipFile(self.epubname, 'w')

        # add the mimetype file uncompressed
        mimetype = 'application/epub+zip'
        fileout = os.path.join(self.outdir,'mimetype')
        file_open(fileout,'wb').write(mimetype.encode('utf-8'))
        nzinfo = ZipInfo('mimetype', compress_type=zipfile.ZIP_STORED)
        outzip.writestr(nzinfo, mimetype)

        self.zipUpDir(outzip,self.outdir,'META-INF')
        if os.path.exists(os.path.join(self.outdir,'Images')):
            self.removeThumbnailImage(os.path.join(self.outdir,'Images'))
            self.zipUpDir(outzip,self.outdir,'Images')

        outzip.write(self.htmlfile, os.path.basename(self.htmlfile), zipfile.ZIP_DEFLATED)
        outzip.write(self.opffile, os.path.basename(self.opffile), zipfile.ZIP_DEFLATED)
        outzip.write(cssname, 'styles.css', zipfile.ZIP_DEFLATED)

        if os.path.exists(os.path.join(self.outdir, 'toc.ncx')):
            outzip.write(os.path.join(self.outdir, 'toc.ncx'), 'toc.ncx', zipfile.ZIP_DEFLATED)
        outzip.close()
        return self.epubname
