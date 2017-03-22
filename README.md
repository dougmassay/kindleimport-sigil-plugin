KindleImport (A Sigil Plugin)
============

Open KindleBooks in Sigil

A Sigil plugin based on/wrapped around the KindleUnpack software (Python based software to unpack Amazon / Kindlegen generated ebooks).

**NOTE: this plugin periodically checks for updated versions by connecting to this Github repository**

Links
=====

* Sigil website is at <http://sigil-ebook.com>
* Sigil support forums are at <http://www.mobileread.com/forums/forumdisplay.php?f=203>
* The KindleImport plugin support thread on MobileRead: <http://www.mobileread.com/forums/showthread.php?t=247087>
* The KindleUnpack python-based software can be found at <https://github.com/kevinhendricks/KindleUnpack>
* python-patch (used to help build the plugin) can be found at <https://github.com/techtonik/python-patch>
* KindleImport plugin MobileRead support thread: <http://www.mobileread.com/forums/showthread.php?t=247087>

Building
========

First, clone the repo:

    $ git clone https://github.com/dougmassay/kindleimport-sigil-plugin.git

Then you need to prepare the source by downloading some core files from the KindleUnpack project. I'm not going to track those files here since they're already maintained in another Git repository. There's a script in the 'setup_tools' folder that will download/patch what you need. Just cd into the 'setup_tools' folder and run the getkucore.py script with Python 2.7+ or 3.4+ (don't try to run the script from outside the 'setup_tools' folder).

    $ cd ./kindleimport-sigil-plugin/setup_tools
    $ python getkucore.py
    $ cd ..

This will create a kindleunpackcore folder. You only need to prepare this folder once -- unless KindleUnpack is updated and you want to use the latest. In that case, just repeat those last 3 steps whenever you want to update the kindleunpackcore files. It will delete the folder and recreate it as necessary.

To create the plugin zip file, run the buildplugin.py script (root of the repository tree) with Python (2 or 3)

    $python buildplugin.py

This will create the KindleImport_vX.X.X.zip file that can then be installed into Sigil's plugin manager.

Using KindleImport
=================
If you're using Sigil v0.9.0 or later on OSX or Windows, all dependencies should already be met so long as you're using the bundled Python interpreter (default).

Linux users will have to make sure that the Tk graphical python module is present if it's not already.  On Debian-based flavors this can be done with "sudo apt-get install python-tk" for python 2.7 or "sudo apt-get install python3-tk" for Python 3.4.

* **Note:** Do not rename any Sigil plugin zip files before attempting to install them

This plugin will work with either Python 3.4+ or Python 2.7+ (defaults to 3.x if both are present).
The absolute minimum version of Sigil required is v0.8.3 (Python must be installed separately prior to v0.9.0)


In addition to being able to unpack/open the KF8 sections of files, it also takes a pretty serious stab at opening the older style mobi-only files (thanks to KevinH for contributions/suggestions on that front). **Also, if the original source package is a part of the file (think kindlegen output) and the original source is an epub, then the plugin will open that instead of using the unpacked version.**

* Please note that there's some atrociously bad markup in many older mobi files (even retail ones), so while the plugin tries its best to whip that markup into some semblance of validity, it's still in your best interest to allow Sigil to correct any issues it may detect upon first opening. *

Configurable preferences (available after first run in the plugin's corresponding json prefs file) are:

* **azw3_epub_version** : a string value that determines whether KF8 books will be imported as epub version 2.0 or epub version 3.0. Defaults to "2" but can be changed manually to "3". Changing this value to "3" will probably cause you nothing but misery before Sigil v0.9.3. **NOTE:** mobi7 formatted books will be unaffected by this preference. They will always be opened as v2.0 epubs. Use the ePub3-itizer plugin if you want those older mobis as ePub3s.

* **use_hd_images** : a true or false (boolean) value (defaults to true). If HD versions of images are present in KF8 books, use those in the resulting epub instead of their lo-rez counterparts.

* **use_src_from_dual_mobi** : a true or false (boolean) value (defaults to true). If the source package is included in the dual-format kindlegen output (and the source is an epub), open that source epub instead of unpacking the KF8 binary. Use false to always unpack.


* **asin_for_kindlegen_plugin** : a true or false (boolean) value (defaults to false). Create a dc:identifier tag from the KindleUnpack metadata that the [kindlegen Sigil plugin](http://www.mobileread.com/forums/showthread.php?t=248629) can then use to force the KF8 portion of a kindlegen-produced, dual-format mobi to have an ASIN.


* **preserve_kindleunpack_meta** : a true or false (boolean) value (defaults to false). KindleUnpack (the core of the KindleImport Plugin) creates a lot of reference metadata that is commented out in the OPF file it creates. Starting with Sigil 0.8.9XX, these comments will not survive when opened with Sigil. Setting this value to "true" will cause this section to be uncommented, so that the metadata tags exist in the OPF file's metadata section in Sigil. It will be up to the users to keep/delete the values they want/don't want.

Get more help at the KindleImport plugin [MobileRead support thread:](http://www.mobileread.com/forums/showthread.php?t=247087)


Contributing / Modifying
============
From here on out, a proficiency with developing / creating Sigil plugins is assumed.
If you need a crash-course, an introduction to creating Sigil plugins is available at
http://www.mobileread.com/forums/showthread.php?t=251452.

Any changes to files in the kindleunpackcore folder will be ignored. The repository is setup to ignore this folder (meaning git won't track changes to them). If you have modifications to suggest for those files, do so upstream at https://github.com/kevinhendricks/KindleUnpack.

Any changes there can be pulled into this repository by running the getkucore.py script in the 'setup_tools' folder.

The core plugin files (this is where most contributors will spend their time) are:

    > gui_utilities.py
    > mobiml2xhtml.py
    > mobi_stuff.py
    > gui_utilities.py
    > plugin.py
    > plugin.xml
    > quickepub.py
    > updatecheck.py
    > utilities.py


Files used for building/maintaining the plugin:

    > buildplugin.py  -- this is used to build the plugin.
    > setup.cfg -- used for flake8 style checking. Use it to see if your code complies.
    > checkversion.xml -- used by automatic update checking (not yet implemented).
    > setup_tools/getkucore.py  -- used to retrieve/prepare upstream KindleUnpack files.
    > setup_tools/pythonpatch.py  -- used by setup.py to apply patches to upstream files if necessary. 
    > setup_tools/kindleunpack.patch  -- patch that will be applied to kindleunpackcore/kindleunpack.py
    > setup_tools/mobi_nav.patch  -- patch that will be applied to kindleunpackcore/mobi_nav.py
    > setup_tools/mobi_ncx.patch  -- patch that will be applied to kindleunpackcore/mobi_ncx.py

Feel free to fork the repository and submit pull requests (or just use it privately to experiment).



License Information
=======

### KindleImport (the Sigil plugin)

    Licensed under the GPLv3.

### [KindleUnpack](https://github.com/kevinhendricks/KindleUnpack)

Based on initial mobipocket version Copyright © 2009 Charles M. Hannum <root@ihack.net>
Extensive Extensions and Improvements Copyright © 2009-2014
By P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding, tkeo.
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3.

### [python-patch](https://github.com/techtonik/python-patch)

Available under the terms of the [MIT license](http://opensource.org/licenses/mit-license.php)

Copyright (c) 2008-2015 anatoly techtonik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
