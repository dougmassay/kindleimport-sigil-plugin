KindleImport (A Sigil Plugin)
============

Open KindleBooks in Sigil

A Sigil plugin based on/wrapped around the KindleUnpack software (Python based software to unpack Amazon / Kindlegen generated ebooks).

Links
=====

* Sigil website is at http://sigil-ebook.com
* The KindleUnpack python-based software can be found at https://github.com/kevinhendricks/KindleUnpack
* python-patch (used to help build the plugin) can be found at https://github.com/techtonik/python-patch

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
    
Contributing / Modifying
============

Any changes to files in the kindleunpackcore folder will be ignored. The repository is setup to ignore this folder (meaning git won't track changes to them). If you have modifications to suggest for those files, do so upstream at https://github.com/kevinhendricks/KindleUnpack.

Any changes there can be pulled into this repository by running the getkucore.py script in the 'setup_tools' folder.

The core plugin files (this is where most contributors will spend their time) are:

    > mobiml2xhtml.py
    > mobi_stuff.py
    > plugin.py
    > plugin.xml
    > quickepub.py
    > utilities.py

Feel free to fork the repository and submit pull requests (or just use it privately to experiment).



License Information
=======

###KindleImport (the Sigil plugin)

    Licensed under the GPLv3.

###KindleUnpack (https://github.com/kevinhendricks/KindleUnpack)

    Based on initial mobipocket version Copyright © 2009 Charles M. Hannum <root@ihack.net>
    Extensive Extensions and Improvements Copyright © 2009-2014 
    By P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding, tkeo.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3.

###python-patch (https://github.com/techtonik/python-patch)

    Available under the terms of the MIT license (http://opensource.org/licenses/mit-license.php)

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