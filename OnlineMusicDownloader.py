#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Online Music Downloader - Download music from some vietnamese music site

+ Auto import from text file
+ Save mp3 link to text file
+ Download with wget or built-in python
+ Auto rename with xml data
+ Auto write tags to mp3 file
+ Auto rename with non unicode file name
"""

import os, sys, re
import optparse
import unicodedata
import eyeD3
from subprocess import call
from urllib import urlretrieve
from NhacSoParser import NhacSoParser
from ZingMP3Parser import ZingMP3Parser
from NhacCuaTuiParser import NhacCuaTuiParser

__author__ = "Thuan.D.T (MrTux)"
__copyright__ = "Copyright (c) 2011 Thuan.D.T (MrTux) "
__credits__ = ["Thuan.D.T"]

__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Thuan.D.T (MrTux)"
__email__ = "mrtux@ubuntu-vn.org"
__status__ = "Development"

def processing(service_url, options):
    """Processing input url."""
    nhacso_url = re.compile('http[s]?://(www.)?(nhacso.net)(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    zing_url = re.compile('http[s]?://(www.)?(mp3.zing.vn)(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    nhaccuatui_url = re.compile('http[s]?://(www.)?(nhaccuatui.com)(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    """Open input file to read data."""
    if(options.input_file is not None):
        try:
            f_input = open(options.input_file, 'r')
            for link in f_input:
                service_url.append(link.strip())
            f_input.close()
        except IOError:
            print "could not open file"
    
    """Open output file to write mp3 link."""
    if(options.output_file is not None):
        try:
            f_output = open(options.output_file, 'w')
        except IOError:
            sys.exit("could not open file to write")

    """Parser and get music data."""
    for url in service_url:
        if(nhacso_url.match(url)):
            song_name, song_artist, song_mp3link = NhacSoParser(url).music_data()
        elif(zing_url.match(url)):
            song_name, song_artist, song_mp3link = ZingMP3Parser(url).music_data() 
        elif(nhaccuatui_url.match(url)):
            song_name, song_artist, song_mp3link = NhacCuaTuiParser(url).music_data()
            
        """Write mp3 link to output file"""
        if(options.output_file is not None):
            for mp3link in song_mp3link:
                    f_output.write("%s\n" % mp3link)
        else:
            """Parser options args and set variable."""
            if(options.download_directory is not None):
                download_directory = options.download_directory
                if(os.path.exists(download_directory) == False):
                    os.mkdir(download_directory)
            else:
                default_download_directory = os.path.join(os.getenv('HOME'), 'Downloads')
                if (os.path.exists(default_download_directory)):
                    download_directory = default_download_directory
                else:
                    os.mkdir(default_download_directory)
                    download_directory = default_download_directory
            if(options.no_unicode is not None):
                for i in range(len(song_name)):
                    song_name[i] = strip_accents(song_name[i])
                    song_artist[i] = strip_accents(song_artist[i])

            write_tag = True
            if(options.no_write_tag is not None):
                    write_tag = False

            if(options.download_accelerator == 'wget'):
                downloadFileWithWget(song_name,
                                     song_artist,
                                     song_mp3link,
                                     write_tag,
                                     download_directory)
            else:
                downloadFileWithPython(song_name,
                                       song_artist,
                                       song_mp3link,
                                       write_tag,
                                       download_directory)

    if(options.output_file is not None):
        f_output.close()

def downloadFileWithPython(song_name,
                           song_artist,
                           song_mp3link,
                           write_tag,
                           download_directory):
    if(write_tag == True):
        tag = eyeD3.Tag()
    for i in range(len(song_name)):
        print "Downloading %s" % (song_name[i])
        mp3_filename = song_name[i].replace('/', '-') + " - " + song_artist[i].replace('/', '-') + ".mp3"
        mp3_filepath = os.path.join(download_directory, mp3_filename)
        urlretrieve(song_mp3link[i], mp3_filepath)

        if(write_tag):
            tag.link(mp3_filepath)
            tag.setTitle(song_name[i].encode('latin-1', 'ignore'))
            tag.setArtist(song_artist[i].encode('latin-1', 'ignore'))
            tag.update()

        print "Done."

def downloadFileWithWget(song_name,
                         song_artist,
                         song_mp3link,
                         write_tag,
                         download_directory):
    wget = ["wget", "-q", "-nd", "-np", "-c", "-r"]
    if(write_tag):
        tag = eyeD3.Tag()

    for i in range(len(song_name)):
        mp3_filename = song_name[i].replace('/', '') + " - " + song_artist[i].replace('/', '') + ".mp3"
        mp3_filepath = os.path.join(download_directory, mp3_filename)
        wget_args = []
        wget_args.append(song_mp3link[i])
        wget_args.append('-O')
        wget_args.append(mp3_filepath)
        print "Downloading %s" % (song_name[i])
        call(wget + wget_args)
        if(write_tag):
            tag.link(mp3_filepath)
            tag.setTitle(song_name[i].encode('latin-1', 'ignore'))
            tag.setArtist(song_artist[i].encode('latin-1', 'ignore'))
            tag.update()
        print "Done."

def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def main():
    """Build the command line option parser."""
    parser = optparse.OptionParser(usage='%prog [options] links')
    parser.add_option("-i", "--input-file",
                      action="store", dest="input_file",
                      type="string", metavar="INPUT-FILE",
                      help="Input file of music links")
    
    parser.add_option("-o", "--output-file",
                      action="store", dest="output_file",
                      type="string", metavar="OUTPUT-FILE",
                      help="Save music links to OUTPUT-FILE")

    parser.add_option("--download-with",
                      action="store", dest="download_accelerator" ,
                      type="string", metavar="PROGRAM",
                      help="Download Accelerator: wget or python")
    
    parser.add_option("--no-unicode",
                      action="store_true", dest="no_unicode" ,
                      help="No use Unicode for file name")
    
    parser.add_option("--no-write-tag",
                      action="store_true", dest="no_write_tag" ,
                      help="No use Unicode for file name")
    
    parser.add_option("-d", "--download-directory",
                      action="store", dest="download_directory",
                      type="string", metavar="DIRECTORY",
                      help="Save download file to DIRECTORY")
    
    """Parser the command line options."""
    service_url = []
    options, args = parser.parse_args(sys.argv)
    for links in args[1:]:
        service_url.append(links)
    processing(service_url, options)

if __name__ == "__main__":
    main()
