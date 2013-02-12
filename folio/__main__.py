#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
    Folio's command-line utility.
"""

import os
import sys
import logging

from folio import Folio, __doc__, __version__
from optparse import OptionParser

def parse():
    usage = "%prog [options] SRC DST"
    version = "%%prog %s" % __version__

    parser = OptionParser(usage=usage, description=__doc__, version=version)
    parser.add_option('-q', '--quiet', dest='verbose',
                      action='store_const', const=logging.CRITICAL + 10,
                      default=logging.INFO,
                      help='suppress all messages')
    parser.add_option('-e', '--encoding', dest='encoding', default='utf-8',
                      help='encoding for output files [defaults to %default]')
    parser.add_option('-R', '--run', dest='command', default='build',
                      action='store_const', const='run',
                      help='run the local web server')
    parser.add_option('-S', '--host', dest='host', default='127.0.0.1',
                      help='hostname to listen on [defaults to %default]')
    parser.add_option('-P', '--port', dest='port', default='8080',
                      help='port of the server [defaults to %default]')

    options, args = parser.parse_args()

    if len(args) == 0:
        parser.error('missing source directory')
    elif len(args) == 1:
        parser.error('missing destination directory')
    elif len(args) > 2:
        parser.error('too many arguments')

    src, dst = args[0], args[1]

    if not os.path.isdir(src):
        parser.error('source must be a directory')

    return options, src, dst

def main():
    options, src, dst = parse()

    proj = Folio(__name__, source_path=src, build_path=dst,
                 encoding=options.encoding)
    proj.logger.addHandler(logging.StreamHandler())
    proj.logger.setLevel(options.verbose)
    proj.build()

    if options.command == 'run':
        proj.run(options.host, int(options.port))

    return 0

if __name__ == '__main__':
    # Support running module as a commandline command.
    # Python 2.5 & 2.6 do: `python -m folio.__main__ [options] [args]`.
    # Python 2.7 & 3.x do: `python -m folio [options] [args]`.
    sys.exit(main()) 