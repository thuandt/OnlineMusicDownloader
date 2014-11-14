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

import os
import sys
import re
import optparse
import unicodedata
import platform
from subprocess import call
from urllib import urlretrieve
from NhacSoParser import NhacSoParser
from ZingMP3Parser import ZingMP3Parser
from NhacCuaTuiParser import NhacCuaTuiParser
from ZingRadioParser import ZingRadioParser

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
    zing_radio_url = re.compile('http[s]?://(www.)?(radio.zing.vn/)(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
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

    """Open output file to write media link."""
    if(options.output_file is not None):
        try:
            f_output = open(options.output_file, 'w')
        except IOError:
            sys.exit("could not open file to write")

    """Parser and get music data."""
    for url in service_url:
        if(nhacso_url.match(url)):
            song_name, song_artist, \
            song_link, song_type = NhacSoParser(url).music_data()
        elif(zing_radio_url.match(url)):
            song_name, song_artist, \
            song_link, song_type = ZingRadioParser(url).music_data()
        elif(zing_url.match(url)):
            song_name, song_artist, \
            song_link, song_type = ZingMP3Parser(url).music_data()
        elif(nhaccuatui_url.match(url)):
            song_name, song_artist, \
            song_link, song_type = NhacCuaTuiParser(url).music_data()

        """Write song_link to output file"""
        if(options.output_file is not None):
            for media_url in song_link:
                f_output.write("%s\n" % media_url)
        else:
            """Parser options args and set variable."""

            # download_directory
            if(options.download_directory is not None):
                download_directory = options.download_directory
                if(os.path.exists(download_directory) == False):
                    os.makedirs(download_directory)
            else:
                if (sys.platform == 'linux2' or sys.platform == 'darwin'):
                    default_download_directory = os.path.join(os.getenv('HOME'),
                                                              'Downloads')
                elif (platform.system() == 'Windows' and
                      platform.release() == 'XP'):
                    default_download_directory = os.path.join(os.getenv('HOME'),
                                                              'My Documents',
                                                              'Downloads')

                elif (platform.system() == 'Windows' and
                     (platform.release() == '7' or
                      platform.release() == 'Vista')):
                    default_download_directory = os.path.join(os.getenv('HOME'),
                                                              'Downloads')
                if (os.path.exists(default_download_directory)):
                    download_directory = default_download_directory
                else:
                    os.makedirs(default_download_directory)
                    download_directory = default_download_directory

            # no_unicode
            if(options.no_unicode is not None):
                for i in range(len(song_name)):
                    song_name[i] = convert_to_ascii(song_name[i])
                    song_artist[i] = convert_to_ascii(song_artist[i])

            # write_tag
            write_tag = False
            if(options.write_tag is not None):
                    write_tag = True

            # download_accelerator
            if(options.download_accelerator == 'wget'):
                downloadFileWithWget(song_name, song_artist,
                                     song_link, song_type,
                                     write_tag, download_directory)
            else:
                downloadFileWithPython(song_name, song_artist,
                                       song_link, song_type,
                                       write_tag, download_directory)

    if(options.output_file is not None):
        f_output.close()


def downloadFileWithPython(song_name, song_artist,
                           song_link, song_type,
                           write_tag, download_directory):
    if(write_tag):
        import eyeD3
        tag = eyeD3.Tag()

    for i in range(len(song_name)):
        """Check None song_link when download."""
        if song_link[i] is not None:
            media_filename = song_name[i].replace('/', '-') + " - " + \
                             song_artist[i].replace('/', '-') + '.' + \
                             song_type[i]
            media_filepath = os.path.join(download_directory, media_filename)

            print "Downloading %s - %s" % (song_artist[i], song_name[i])
            urlretrieve(song_link[i], media_filepath)

            if(write_tag) and (song_type[i] == 'mp3'):
                tag.link(media_filepath)
                tag.setTitle(convert_to_ascii(song_name[i]))
                tag.setArtist(convert_to_ascii(song_artist[i]))
                tag.update()

            print "Done."
        else:
            print "Can't find media url for %s - %s " % (song_artist[i], song_name[i])


def downloadFileWithWget(song_name, song_artist,
                         song_link, song_type,
                         write_tag, download_directory):
    wget = ["wget", "-q", "-nd", "-np", "-c", "-r"]

    if(write_tag):
        import eyeD3
        tag = eyeD3.Tag()

    for i in range(len(song_name)):
        """Check None song_link when download."""
        if song_link[i] is not None:
            media_filename = song_name[i].replace('/', '') + " - " + \
                             song_artist[i].replace('/', '') + '.' + \
                             song_type[i]
            media_filepath = os.path.join(download_directory, media_filename)

            wget_args = []
            wget_args.append(song_link[i])
            wget_args.append('-O')
            wget_args.append(media_filepath)

            print "Downloading %s - %s" % (song_artist[i], song_name[i])
            call(wget + wget_args)

            if(write_tag) and (song_type[i] == 'mp3'):
                tag.link(media_filepath)
                tag.setTitle(convert_to_ascii(song_name[i]))
                tag.setArtist(convert_to_ascii(song_artist[i]))
                tag.update()

            print "Done."
        else:
            print "Can't find media url for %s - %s " % (song_artist[i], song_name[i])


def convert_to_ascii(s):
    """convert unicode to ascii"""
    # s = re.sub(u'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    # s = re.sub(u'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    # s = re.sub(u'èéẹẻẽêềếệểễ', 'e', s)
    # s = re.sub(u'ÈÉẸẺẼÊỀẾỆỂỄ', 'E', s)
    # s = re.sub(u'òóọỏõôồốộổỗơờớợởỡ', 'o', s)
    # s = re.sub(u'ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ', 'O', s)
    # s = re.sub(u'ìíịỉĩ', 'i', s)
    # s = re.sub(u'ÌÍỊỈĨ', 'I', s)
    # s = re.sub(u'ùúụủũưừứựửữ', 'u', s)
    # s = re.sub(u'ƯỪỨỰỬỮÙÚỤỦŨ', 'U', s)
    # s = re.sub(u'ỳýỵỷỹ', 'y', s)
    # s = re.sub(u'ỲÝỴỶỸ', 'Y', s)
    s = re.sub(u'Đ', 'D', s)
    s = re.sub(u'đ', 'd', s)
    return unicodedata.normalize('NFKD', unicode(s)).encode('ASCII', 'ignore')


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
                      action="store", dest="download_accelerator",
                      type="string", metavar="PROGRAM",
                      help="Download Accelerator: wget or python")

    parser.add_option("--no-unicode",
                      action="store_true", dest="no_unicode",
                      help="No use Unicode for file name")

    parser.add_option("--write-tag",
                      action="store_true", dest="write_tag",
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
    try:
        main()
    except KeyboardInterrupt:
        print "\nFile download has been canceled"
