#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# XMLBible.py
#   Last modified: 2013-04-10 by RJH (also update versionString below)
#
# Module handling simple XML Bibles
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
Module reading and loading simple XML Bibles such as OpenSong Bibles:
    <?xml version="1.0" encoding="ISO-8859-1"?>
    <bible>
    <b n="Genesis">
    <c n="1">
    <v n="1">In the beginning God created the heaven and the earth.</v>
    <v n="2">And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.</v>
"""

progName = "XML Bible format handler"
versionString = "0.21"

import logging, os
from gettext import gettext as _
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

import Globals
from BibleOrganizationalSystems import BibleOrganizationalSystem
from InternalBible import InternalBible
from InternalBibleBook import InternalBibleBook


class XMLBible( InternalBible ):
    """
    Class for reading, validating, and converting XMLBible XML.
    """
    treeTag = 'bible'
    bookTag = 'b'
    chapterTag = 'c'
    verseTag = 'v'


    def __init__( self, sourceFilepath, givenName=None, encoding='utf-8', logErrorsFlag=False  ):
        """
        Constructor: just sets up the XML Bible file converter object.
        """
         # Setup and initialise the base class first
        self.objectType = "XML"
        self.objectNameString = "XML Bible object"
        InternalBible.__init__( self )

        # Now we can set our object variables
        self.sourceFilepath, self.givenName, self.encoding, self.logErrorsFlag = sourceFilepath, givenName, encoding, logErrorsFlag

        self.tree = None # Will hold the XML data

        # Get the data tables that we need for proper checking
        #self.ISOLanguages = ISO_639_3_Languages().loadData()
        self.genericBOS = BibleOrganizationalSystem( "GENERIC-KJV-66-ENG" )

        # Do a preliminary check on the readability of our file
        if not os.access( self.sourceFilepath, os.R_OK ):
            print( "XMLBible: File '{}' is unreadable".format( self.sourceFilepath ) )

        self.name = self.givenName
        #if self.name is None:
            #pass
    # end of XMLBible.__init__


    def load( self ):
        """
        Load a single source XML file and load book elements.
        """
        if Globals.verbosityLevel > 2: print( _("Loading {}...").format( self.sourceFilepath ) )
        self.tree = ElementTree().parse( self.sourceFilepath )
        assert( len ( self.tree ) ) # Fail here if we didn't load anything at all

        # Find the main (bible) container
        if self.tree.tag == XMLBible.treeTag:
            location = "XML file"
            Globals.checkXMLNoText( self.tree, location, '4f6h' )
            Globals.checkXMLNoTail( self.tree, location, '1wk8' )

            name = shortName = None
            for attrib,value in self.tree.items():
                if attrib=="n":
                    name = value
                elif attrib=="sn":
                    shortName = value
                else: logging.warning( "Unprocessed '{}' attribute ({}) in main element".format( attrib, value ) )

            # Find the submain (book) containers
            for element in self.tree:
                if element.tag == XMLBible.bookTag:
                    sublocation = "book in " + location
                    Globals.checkXMLNoText( element, sublocation, 'g3g5' )
                    Globals.checkXMLNoTail( element, sublocation, 'd3f6' )
                    self.__validateAndExtractBook( element )
                elif element.tag == 'OT':
                    pass
                elif element.tag == 'NT':
                    pass
                else: logging.error( "Expected to find '{}' but got '{}'".format( XMLBible.bookTag, element.tag ) )
        else: logging.error( "Expected to load '{}' but got '{}'".format( XMLBible.treeTag, self.tree.tag ) )
    # end of XMLBible.load


    def __validateAndExtractBook( self, book ):
        """
        Check/validate and extract book data from the given XML book record
            finding chapter subelements.
        """

        if Globals.verbosityLevel > 3: print( _("Validating XML book...") )

        # Process the div attributes first
        BBB = bookName = None
        for attrib,value in book.items():
            if attrib=="n":
                bookName = value
            else: logging.warning( "Unprocessed '{}' attribute ({}) in book element".format( attrib, value ) )
        if bookName:
            BBB = self.genericBOS.getBBB( bookName )
            if Globals.verbosityLevel > 2: print( _("Validating {} {}...").format( BBB, bookName ) )

        thisBook = InternalBibleBook( BBB, self.logErrorsFlag )
        thisBook.objectType = "XML"
        thisBook.objectNameString = "XML Bible Book object"
        #thisBook.sourceFilepath = self.sourceFilepath
        for element in book:
            if element.tag == XMLBible.chapterTag:
                sublocation = "chapter in {}".format( BBB )
                Globals.checkXMLNoText( element, sublocation, 'j3jd' )
                Globals.checkXMLNoTail( element, sublocation, 'al1d' )
                self.__validateAndExtractChapter( BBB, thisBook, element )
            else: logging.error( "Expected to find '{}' but got '{}'".format( XMLBible.chapterTag, element.tag ) )

        if BBB:
            if Globals.verbosityLevel > 2: print( "  Saving {} into results...".format( BBB ) )
            self.saveBook( BBB, thisBook )
    # end of XMLBible.__validateAndExtractBook


    def __validateAndExtractChapter( self, BBB, thisBook, chapter ):
        """
        Check/validate and extract chapter data from the given XML book record
            finding and saving chapter numbers and
            finding and saving verse elements.
        """

        if Globals.verbosityLevel > 3: print( _("Validating XML chapter...") )

        # Process the div attributes first
        chapterNumber = numVerses = None
        for attrib,value in chapter.items():
            if attrib=="n":
                chapterNumber = value
            elif attrib=="VERSES":
                numVerses = value
            else: logging.warning( "Unprocessed '{}' attribute ({}) in chapter element".format( attrib, value ) )
        if chapterNumber:
            #print( BBB, 'c', chapterNumber )
            thisBook.appendLine( 'c', chapterNumber )
        else: logging.error( "Missing 'n' attribute in chapter element for BBB".format( BBB ) )

        for element in chapter:
            if element.tag == XMLBible.verseTag:
                sublocation = "verse in {} {}".format( BBB, chapterNumber )
                Globals.checkXMLNoTail( element, sublocation, 'l5ks' )
                Globals.checkXMLNoSubelements( element, sublocation, '5f7h' )
                verseNumber = toVerseNumber = None
                for attrib,value in element.items():
                    if attrib=="n":
                        verseNumber = value
                    elif attrib=="t":
                        toVerseNumber = value
                    else: logging.warning( "Unprocessed '{}' attribute ({}) in verse element".format( attrib, value ) )
                assert( verseNumber )
                #thisBook.appendLine( 'v', verseNumber )
                vText = element.text
                if not vText:
                    logging.warning( "{} {}:{} has no text".format( BBB, chapterNumber, verseNumber ) )
                if vText: # This is the main text of the verse (follows the verse milestone)
                    #print( "{} {}:{} '{}'".format( BBB, chapterNumber, verseNumber, vText ) )
                    thisBook.appendLine( 'v', verseNumber + ' ' + vText )
            else: logging.error( "Expected to find '{}' but got '{}'".format( XMLBible.verseTag, element.tag ) )
    # end of XMLBible.__validateAndExtractChapter
# end of XMLBible class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Configure basic logging
    logging.basicConfig( format='%(levelname)s: %(message)s', level=logging.INFO ) # Removes the unnecessary and unhelpful 'root:' part of the logged messages

    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    #parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 0: print( "{} V{}".format( progName, versionString ) )

    testFolder = "/mnt/Data/Work/Bibles/Formats/OpenSong/"
    single = ( "KJV.xmm", )
    good = ( "KJV.xmm", "AMP.xmm", "Chinese_SU.xmm", "Contemporary English Version.xmm", "ESV", "Italiano", "MKJV", \
        "MSG.xmm", "NASB.xmm", "NIV", "NKJV.xmm", "NLT", "telugu.xmm", )
    nonEnglish = ( "BIBLIA warszawska", "Chinese Union Version Simplified.txt", "hun_karoli", "KNV_HU", "LBLA.xmm", \
        "Nowe Przymierze", "NVI.xmm", "NVI_PT", "PRT-IBS.xmm", "RV1960", "SVL.xmm", "UJPROT_HU", "vdc", \
        "Vietnamese Bible.xmm", )
    bad = ( "EPS99", )

    for testFilename in good:
        testFilepath = os.path.join( testFolder, testFilename )

        # Demonstrate the XML Bible class
        if Globals.verbosityLevel > 1: print( "\nDemonstrating the XML Bible class..." )
        if Globals.verbosityLevel > 0: print( "  Test filepath is '{}'".format( testFilepath ) )
        xb = XMLBible( testFilepath )
        xb.load() # Load and process the XML
        print( xb ) # Just print a summary
        #print( xb.books['JDE']._processedLines )
        if 1: # Test verse lookup
            import VerseReferences
            for reference in ( ('OT','GEN','1','1'), ('OT','GEN','1','3'), ('OT','PSA','3','0'), ('OT','PSA','3','1'), \
                                ('OT','DAN','1','21'),
                                ('NT','MAT','3','5'), ('NT','JDE','1','4'), ('NT','REV','22','21'), \
                                ('DC','BAR','1','1'), ('DC','MA1','1','1'), ('DC','MA2','1','1',), ):
                (t, b, c, v) = reference
                if t=='OT' and len(xb)==27: continue # Don't bother with OT references if it's only a NT
                if t=='NT' and len(xb)==39: continue # Don't bother with NT references if it's only a OT
                if t=='DC' and len(xb)<=66: continue # Don't bother with DC references if it's too small
                svk = VerseReferences.simpleVerseKey( b, c, v )
                #print( svk, ob.getVerseDataList( reference ) )
                print( reference, svk.getShortText(), xb.getVerseText( svk ) )
# end of main

if __name__ == '__main__':
    main()
# end of XMLBible.py