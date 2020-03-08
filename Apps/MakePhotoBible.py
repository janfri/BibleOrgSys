#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# MakePhotoBible.py
#
# Command-line app to export a PhotoBible.
#
# Copyright (C) 2015-2017 Robert Hunt
# Author: Robert Hunt <Freely.Given.org@gmail.com>
# License: See gpl-3.0.txt
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
A short command-line app as part of BOS (Bible Organisational System) demos.
This app inputs any known type of Bible file(s) [set inputFolder below]
    and then exports a PhotoBible in the (default) OutputFiles folder
        (inside the folder where you installed the BOS).

Of course, you must already have Python3 installed on your system.
    (Probably installed by default on most modern Linux systems.)
For the PhotoBible export, you also need ImageMagick installed.

Note that this app MUST BE RUN FROM YOUR BOS folder,
    e.g., using the command:
        Apps/MakePhotoBible.py

You can discover the version with
        Apps/MakePhotoBible.py --version

You can discover the available command line parameters with
        Apps/MakePhotoBible.py --help

    e.g., for verbose mode
        Apps/MakePhotoBible.py --verbose
    or
        Apps/MakePhotoBible.py -v

This app also demonstrates how little code is required to use the BOS
    to load a Bible (in any of a large range of formats -- see UnknownBible.py)
    and then to export it in your desired format (see options in BibleWriter.py).

The (Python3) BOS is developed and well-tested on Linux (Ubuntu)
    but also runs on Windows (although not so well tested).
(The PhotoBible export is unlikely to work straight away on Windows
    because it calls external programs outside of Python to make the JPEG files,
    but most other Bible exports should work fine.)

Because it repeatedly runs external programs (ImageMagick), the PhotoBible export
    runs several orders of magnitude slower than most other Bible exports.
"""

# You must specify where to find a Bible to read --
#   this can be either a relative path (like my example where ../ means go to the folder above)
#   or an absolute path (which would start with / or maybe ~/ in Linux).
# Normally this is the only line in the program that you would need to change.
inputFolder = BibleOrgSysGlobals.PARALLEL_RESOURCES_BASE_FOLDERPATH.joinpath( '../../../../../mnt/SSDs/Matigsalug/Bible/MBTV/' ) # Set your own here


from gettext import gettext as _

lastModifiedDate = '2019-01-29' # by RJH
shortProgramName = "MakePhotoBible"
programName = "Make PhotoBible"
programVersion = '0.23'
programNameVersion = f'{programName} v{programVersion}'
programNameVersionDate = f'{programNameVersion} {_("last modified")} {lastModifiedDate}'

import os

# Allow the system to find the BOS even when the app is down in its own folder
if __name__ == '__main__':
    import sys
    sys.path.append( os.path.abspath( os.path.join(os.path.dirname(__file__), '../BibleOrgSys/') ) ) # So we can run it from the folder above and still do these imports
    sys.path.append( os.path.abspath( os.path.join(os.path.dirname(__file__), '../') ) ) # So we can run it from the folder above and still do these imports

import BibleOrgSysGlobals
from UnknownBible import UnknownBible



def main():
    """
    This is the main program for the app
        which just tries to open and load some kind of Bible file(s)
            from the inputFolder that you specified
        and then export a PhotoBible (in the default OutputFiles folder).

    Note that the standard verbosityLevel is 2:
        -s (silent) is 0
        -q (quiet) is 1
        -i (information) is 3
        -v (verbose) is 4.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0:
        print( programNameVersion )
        print( "\n{}: processing input folder {!r} …".format( shortProgramName, inputFolder ) )

    # Try to detect and read/load the Bible file(s)
    unknownBible = UnknownBible( inputFolder ) # Tell it the folder to start looking in
    loadedBible = unknownBible.search( autoLoadAlways=True, autoLoadBooks=True ) # Load all the books if we find any
    if BibleOrgSysGlobals.verbosityLevel > 2: print( unknownBible ) # Display what Bible typed we found
    if BibleOrgSysGlobals.verbosityLevel > 1: print( loadedBible ) # Show how many books we loaded

    # If we were successful, do the export
    if loadedBible is not None:
        if BibleOrgSysGlobals.strictCheckingFlag: loadedBible.check()
        if BibleOrgSysGlobals.verbosityLevel > 0:
            print( "\n{}: starting export (may take up to 60 minutes)…".format( shortProgramName ) )

        # We only want to do the PhotoBible export (from the BibleWriter.py module)
        result = loadedBible.toPhotoBible() # Export as a series of small JPEG files (for cheap non-Java camera phones)
        # However, you could easily change this to do all exports
        #result = loadedBible.doAllExports( wantPhotoBible=True, wantODFs=True, wantPDFs=True )
        # Or you could choose a different export, for example:
        #result = loadedBible.toOSISXML()
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "  Result was: {}".format( result ) )
        print(f"Output should be in {os.path.join(os.getcwd(), BibleOrgSysGlobals.DEFAULT_OUTPUT_FOLDERPATH)} folder.")
# end of main

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic Bible Organisational System (BOS) set-up
    parser = BibleOrgSysGlobals.setup( programName, programVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    main()

    BibleOrgSysGlobals.closedown( programName, programVersion )
# end of MakePhotoBible.py
