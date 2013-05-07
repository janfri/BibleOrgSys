#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# SwordResources.py
#   Last modified: 2013-05-03 (also update versionString below)
#
# Module handling Sword resources using the Sword engine
#
# Copyright (C) 2013 Robert Hunt
# Author: Robert Hunt <robert316@users.sourceforge.net>
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
Module handling content modules produced for Crosswire Sword.
This module uses the Sword engine (libsword) via the Python SWIG bindings.
(If you don't want to install that, consider our SwordModules module.)
"""

progName = "Sword resource handler"
versionString = "0.02"


#from singleton import singleton
import os, logging
from gettext import gettext as _
#from collections import OrderedDict

import Globals
from VerseReferences import SimpleVerseKey


try:
    import Sword
    SwordType = "CrosswireLibrary"
except: # Sword library (dll and python bindings) seem to be not available
    if 0: # Warn the user that this won't work
        logging.critical( _("You need to install the Sword library on your computer in order to use this module.") )
        logging.info( _("Alternatively, you can try the all-Python SwordModules module.") )
        sys.exit( 1 )
    else: # Use our own Python3 code instead
        import SwordModules
        SwordType = "OurCode"



class SwordKey( SimpleVerseKey ):
    #def __init__( self, BBB, c, v, s=None ):
        #if s is None: s = ''
        #self.myKey = BBB, c, v, s

    #def __getitem__( self, keyIndex ):
        #return self.myKey[keyIndex]

    #def __str__( self ):
        #return "{} {}:{}{}".format( self.myKey[0], self.myKey[1], self.myKey[2], self.myKey[3] )

    #def getShortText( self ):
        #return "{} {}:{}{}".format( self.myKey[0], self.myKey[1], self.myKey[2], self.myKey[3] )

    def getChapter( self ):
        return self.getChapterNumberInt()

    def getVerse( self ):
        return self.getVerseNumberInt()
# end of class SwordKey


class SwordInterface():
    def __init__( self ):
        if SwordType == "CrosswireLibrary":
            self.library = Sword.SWMgr()
            #self.keyCache = {}
            #self.verseCache = {}
        else:
            self.library = SwordModules.SwordModules() # Loads all of conf files that it can find
            #print( self.library )

    def getModule( self, moduleAbbreviation='KJV' ):
        if Globals.debugFlag: print( "SwordResources.getModule({})".format( moduleAbbreviation ) )
        if SwordType == "CrosswireLibrary":
            #print( "gM", module.getName() )
            return self.library.getModule( moduleAbbreviation )
        else:
            return self.library.loadModule( moduleAbbreviation )
    # end of SwordInterface.getModule


    def makeKey( self, BBB, C, V ):
        #if Globals.debugFlag: print( "SwordResources.makeKey({})".format( BCV ) )
        #if BCV  in self.keyCache:
            #print( "Cached", BCV )
            #return self.keyCache[BCV]
        if SwordType == "CrosswireLibrary":
            B = Globals.BibleBooksCodes.getOSISAbbreviation( BBB )
            refString = "{} {}:{}".format( B, C, V )
            #print( 'refString', refString )
            verseKey = Sword.VerseKey( refString )
            #self.keyCache[BCV] = verseKey
            return verseKey
        else:
            return SwordKey( BBB, C, V )
    # end of SwordInterface.makeKey


    def getVerseData( self, module, key ):
        """
        Returns a list of 5-tuples, e.g.,
            [
            ('c', 'c', '1', '1', []),
            ('c#', 'c', '1', '1', []),
            ('v', 'v', '1', '1', []),
            ('v~', 'v~', 'In the beginning God created the heavens and the earth.',
                                    'In the beginning God created the heavens and the earth.', [])
            ]
        """
        if SwordType == "CrosswireLibrary":
            try: verseText = module.stripText( key )
            except UnicodeDecodeError:
                print( "Can't decode utf-8 text of {} {}".format( module.getName(), key.getShortText() ) )
                return
            verseData = []
            c, v = str(key.getChapter()), str(key.getVerse())
            # Prepend the verse number since Sword modules don't contain that info in the data
            if v=='1': verseData.append( ('c#','c', c, c, [],) )
            verseData.append( ('v','v', v, v, [],) )
            verseData.append( ('v~','v~', verseText, verseText, [],) )
        else:
            verseData = module.getBCVRef( key )
            #print( "gVD", module.getName(), key, verseData )
            if verseData is None:
                print( "SI.gVD no VD", module.getName(), key, verseData )
                assert( key.getChapter()==0 or key.getVerse()==0 )
            else:
                assert( isinstance( verseData, list ) )
                assert( 1 <= len(verseData) <= 5 )
        #print( verseData ); halt
        return verseData
    # end of SwordInterface.getVerseData


    def getVerseText( self, module, key ):
        #cacheKey = (module.getName(), key.getShortText())
        #if cacheKey in self.verseCache:
            #print( "Cached", cacheKey )
            #return self.verseCache[cacheKey]
        #if Globals.debugFlag: print( "SwordResources.getVerseText({},{})".format( module.getName(), key.getText() ) )
        if SwordType == "CrosswireLibrary":
            try: verseText = module.stripText( key )
            except UnicodeDecodeError:
                print( "Can't decode utf-8 text of {} {}".format( module.getName(), key.getShortText() ) )
                return ''
        else:
            verseData = module.getBCVRef( key )
            #print( "gVT", module.getName(), key, verseData )
            assert( isinstance( verseData, list ) )
            assert( 2 <= len(verseData) <= 5 )
            verseText = ''
            for marker,originalMarker,text,cleanText,extras in verseData:
                if marker == 'c': pass # Ignore
                elif marker == 'p': verseText += '¶' + cleanText
                elif marker == 'm': verseText += '§' + cleanText
                elif marker == 'v': pass # Ignore
                elif marker == 'v~': verseText += cleanText
                else: print( "Unknown marker", marker, cleanText ); halt
        #self.verseCache[cacheKey] = verseText
        #print( module.getName(), key.getShortText(), "'"+verseText+"'" )
        return verseText
    # end of SwordInterface.getVerseText
# end of class SwordInterface


def getBCV( BCV, moduleAbbreviation='KJV' ): # Very slow -- for testing only
    if Globals.debugFlag: print( "SwordResources.getBCV({},{})".format( BCV, moduleAbbreviation ) )
    library = Sword.SWMgr()
    module = library.getModule( moduleAbbreviation )
    refString = "{} {}:{}".format( BCV[0][:3], BCV[1], BCV[2] )
    #print( 'refString', refString )
    return module.stripText( Sword.VerseKey( refString ) )
# end of getBCV



def demo():
    """
    Sword
    """
    # Configure basic logging
    logging.basicConfig( format='%(levelname)s: %(message)s', level=logging.INFO ) # Removes the unnecessary and unhelpful 'root:' part of the logged messages

    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    #parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 0: print( "{} V{}".format( progName, versionString ) )

    #print( "\ndir Sword", dir(Sword) )

    if SwordType == "CrosswireLibrary":
        print( "\ndir Sword.SWVersion()", dir(Sword.SWVersion()) )
        print( "Version", Sword.SWVersion().getText() )
        print( "Versions", Sword.SWVersion().major, Sword.SWVersion().minor, Sword.SWVersion().minor2, Sword.SWVersion().minor3 ) # ints

        library = Sword.SWMgr()
        #print( "\ndir library", dir(library) )
        #print( "\nlibrary getHomeDir", library.getHomeDir().getRawData() )

    def Find( attribute ):
        """ Search for methods and attributes """
        print( "\nSearching for attribute '{}'...".format( attribute ) )
        found = False
        AA = attribute.upper()
        for thing in dir(Sword):
            BB = thing.upper()
            if BB.startswith(AA): print( "  Have {} in Sword".format( thing ) ); found = True
        for thing in dir(Sword.SWVersion()):
            BB = thing.upper()
            if BB.startswith(AA): print( "  Have {} in SWVersion".format( thing ) ); found = True
        for thing in dir(Sword.SWMgr()):
            BB = thing.upper()
            if BB.startswith(AA): print( "  Have {} in SWMgr".format( thing ) ); found = True
        module = library.getModule( "KJV" )
        for thing in dir(module):
            BB = thing.upper()
            if BB.startswith(AA): print( "  Have {} in SWModule".format( thing ) ); found = True
        for thing in dir(Sword.SWKey()):
            BB = thing.upper()
            if BB.startswith(AA): print( "  Have {} in SWKey".format( thing ) ); found = True
        for thing in dir(Sword.VerseKey()):
            BB = thing.upper()
            if BB.startswith(AA): print( "  Have {} in VerseKey".format( thing ) ); found = True
        #for thing in dir(Sword.InstallMgr()):
            #BB = thing.upper()
            #if BB.startswith(AA): print( "  Have {} in InstallMgr".format( thing ) ); found = True
        for thing in dir(Sword.LocaleMgr()):
            BB = thing.upper()
            if BB.startswith(AA): print( "  Have {} in LocaleMgr".format( thing ) ); found = True
        for thing in dir(Sword.SWFilterMgr()):
            BB = thing.upper()
            if BB.startswith(AA): print( "  Have {} in SWFilterMgr".format( thing ) ); found = True
        if not found: print( " Sorry, '{}' not found.".format( attribute ) )
    # end of Find

    if 0: # Install manager
        print( "\nINSTALL MANAGER" )
        im = Sword.InstallMgr() # FAILS
        print( "\ndir im", im, dir(im) )

    if 0: # Locale manager
        print( "\nLOCALE MANAGER" )
        lm = Sword.LocaleMgr()
        print( "dir lm", lm, dir(lm) )
        print( "default {}".format( lm.getDefaultLocaleName() ) )
        print( "available {}".format( lm.getAvailableLocales() ) ) # Gives weird result: "available ()"
        print( "locale {}".format( lm.getLocale( "en" ) ) ) # Needs a string parameter but why does it return None?

    if 0: # try filters
        print( "\nFILTER MANAGER" )
        fm = Sword.SWFilterMgr()
        print( "\ndir filters", dir(fm) )

    if SwordType == "CrosswireLibrary":
        # Get a list of available module names and types
        print( "\n{} modules are installed.".format( len(library.getModules()) ) )
        for j,moduleBuffer in enumerate(library.getModules()):
            moduleID = moduleBuffer.getRawData()
            module = library.getModule( moduleID )
            if 0:
                print( "{} {} ({}) {} '{}'".format( j, module.getName(), module.getType(), module.getLanguage(), module.getEncoding() ) )
                try: print( "    {} '{}' {} {}".format( module.getDescription(), module.getMarkup(), module.getDirection(), "" ) )
                except UnicodeDecodeError: print( "   Description is not Unicode!" )
        #print( "\n", j, "dir module", dir(module) )

        # Try some modules
        mod1 = library.getModule( "KJV" )
        print( "\nmod1 {} ({}) '{}'".format( mod1.getName(), mod1.getType(), mod1.getDescription() ) )
        mod2 = library.getModule( "ASV" )
        print( "\nmod2 {} ({}) '{}'".format( mod2.getName(), mod2.getType(), mod2.getDescription() ) )
        mod3 = library.getModule( "WEB" )
        print( "\nmod3 {} ({}) '{}'".format( mod3.getName(), mod3.getType(), mod3.getDescription() ) )
        strongsGreek = library.getModule( "StrongsGreek" )
        print( "\nSG {} ({}) '{}'\n".format( strongsGreek.getName(), strongsGreek.getType(), strongsGreek.getDescription() ) )
        strongsHebrew = library.getModule( "StrongsHebrew" )
        print( "\nSH {} ({}) '{}'\n".format( strongsHebrew.getName(), strongsHebrew.getType(), strongsHebrew.getDescription() ) )
        print()

        # Try a sword key
        sk = Sword.SWKey( "H0430" )
        #print( "\ndir sk", dir(sk) )

        # Try a verse key
        vk = Sword.VerseKey( "Jn 3:16" )
        #print( "\ndir vk", dir(vk) )
        #print( "val", vk.validateCurrentLocale() ) # gives None
        print( "getInfo", vk.getLocale(), vk.getBookCount(), vk.getBookMax(), vk.getIndex(), vk.getVersificationSystem() )
        print( "getBCV {}({}/{}) {}/{}:{} in '{}'({})/{}".format( vk.getBookName(), vk.getBookAbbrev(), vk.getOSISBookName(), vk.getChapter(), vk.getChapterMax(), vk.getVerse(), repr(vk.getTestament()), vk.getTestamentIndex(), vk.getTestamentMax() ) )
        print( "getText {} {} {} {} '{}'".format( vk.getOSISRef(), vk.getText(), vk.getRangeText(), vk.getShortText(), vk.getSuffix() ) )
        #print( "bounds {} {}".format( vk.getLowerBound(), vk.getUpperBound() ) )

        if 0: # Set a filter HOW DO WE DO THIS???
            rFs = mod1.getRenderFilters()
            print( mod1.getRenderFilters() )
            mod1.setRenderFilter()

        print( "\n{} {}: {}".format( mod1.getName(), "Jonny 1:1", mod1.renderText( Sword.VerseKey("Jn 1:1") ) ) )
        mod1.increment()
        print( "\n{} {}: {}".format( mod1.getName(), mod1.getKey().getText(), mod1.stripText(  ) ) )
        mod1.increment()
        print( "\n{} {}: {}".format( mod1.getName(), mod1.getKey().getText(), mod1.renderText(  ) ) )
        print( "\n{} {}: {}".format( mod2.getName(), vk.getText(), mod2.renderText( vk ) ) )
        print( "\n{} {}: {}".format( mod3.getName(), vk.getText(), mod3.renderText( vk ) ) )
        print( "\n{} {}: {}".format( mod3.getName(), vk.getText(), mod3.renderText( vk ) ) )

        print( "\n{} {}: {}".format( strongsGreek.getName(), sk.getText(), strongsGreek.renderText( Sword.SWKey("G746") ) ) )
        print( "\n{} {}: {}".format( strongsHebrew.getName(), sk.getText(), strongsHebrew.renderText( sk ) ) )

        if 0: # Get all vernacular booknames
            # VerseKey vk; while (!vk.Error()) { cout << vk.getBookName(); vk.setBook(vk.getBook()+1); }
            vk = Sword.VerseKey()
            while vk.popError()=='\x00':
                print( "bookname", vk.getBookName() )
                booknumber = int( bytes( vk.getBook(),'utf-8' )[0] )
                vk.setBook( booknumber + 1 )

        if 0: # Get booknames by testament (from http://www.crosswire.org/wiki/DevTools:Code_Examples)
            vk = Sword.VerseKey()
            for t in range( 1, 2+1 ):
                vk.setTestament( t )
                for i in range( 1, vk.getBookMax()+1 ):
                    vk.setBook( i )
                    print( t, i, vk.getBookName() )

        # Try a tree key on a GenBook
        module = library.getModule( "Westminster" )
        print( "\nmodule {} ({}) '{}'".format( module.getName(), module.getType(), module.getDescription() ) )
        def getGenBookTOC( tk, parent ):
            if tk is None: # obtain one from the module
                tk = Sword.TreeKey_castTo( module.getKey() ) # Only works for gen books
            if tk and tk.firstChild():
                while True:
                    print( " ", tk.getText() )
                    # Keep track of the information for custom implementation
                    #Class *item = storeItemInfoForLaterUse(parent, text);
                    item = (parent) # temp ....................
                    if tk.hasChildren():
                        print( "  Getting children..." )
                        getGenBookTOC( tk, item )
                    if not tk.nextSibling(): break
        # end of getGenBookTOC
        getGenBookTOC( None, None )

    #Find( "sw" ) # lots!
    #Find( "store" ) # storeItemInfoForLaterUse
    #Find( "getGlobal" ) # should be lots
# end of demo

if __name__ == '__main__':
    demo()
# end of SwordResources.py