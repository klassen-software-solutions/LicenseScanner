#!/usr/bin/env python3

"""Scans a directory to determine the licenses of its dependancies."""

import argparse
import datetime
import json
import logging
import os
import pathlib
import sys

from .kss_prereqs_scanner import KSSPrereqsScanner
from .manual_scanner import ManualScanner
from .swift_scanner import SwiftModuleScanner
from . import __version__


def _parse_command_line(args: list):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true', help='Show debugging information')
    parser.add_argument('--version', action='store_true', help='Show version number and then exit')
    parser.add_argument('--directory',
                        default='.',
                        help='Directory to be scanned (defaults to the current working directory)')
    parser.add_argument('--name',
                        help='Name of module to be scanned (default is the basename of the '
                        + 'directory).')
    parser.add_argument('--output',
                        default='Dependencies/prereqs-licenses.json',
                        help='Output file, relative to the scanned directory. (Default is '
                        + '"Dependencies/prereqs-licenses.json")')
    parser.add_argument('--manual-licenses',
                        default='manual-licenses.json',
                        metavar='FILENAME',
                        help='File containing manually generated license entries, within '
                        + 'the scanned directory. Default is "manual-licenses.json")')
    return parser.parse_args(args)


def _write_licenses(filename: str, licenses: dict, metadata: dict):
    outputdir = os.path.dirname(filename)
    if outputdir:
        pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)
    data = {
        'dependencies': sorted(licenses.values(), key=lambda x: x['moduleName']),
        'generated': metadata
    }
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

def _generated_metadata():
    args = ""
    if len(sys.argv) > 1:
        args = " %s" % ' '.join(sys.argv[1:])
    metadata = {
        'time': datetime.datetime.now().astimezone().isoformat(),
        'process': 'license-scanner%s' % args,
        'project': os.path.basename(os.getcwd())
    }
    return metadata



def scan(args: list = None):
    """Main entry point.

    Parameters:
        args: list of strings specifying the arguments. If None then sys.argv will be used.
    """

    options = _parse_command_line(args)
    if options.version:
        print(__version__)
        sys.exit()

    logging.getLogger().setLevel(logging.DEBUG if options.verbose else logging.INFO)

    if not os.path.isdir(options.directory):
        raise FileNotFoundError(options.directory)

    cwd = os.getcwd()
    directory = options.directory
    if directory == ".":
        directory = cwd
    modulename = options.name or os.path.basename(directory)
    outputfile = options.output
    manualentries = options.manual_licenses

    logging.info("Scanning for licenses in '%s'", directory)
    logging.debug("  identifying module as '%s'", modulename)
    logging.debug("  will write output to '%s'", outputfile)
    logging.debug("  will look for manual entries in '%s'", manualentries)

    try:
        os.chdir(directory)
        licenses = {}
        scanners = [ManualScanner(modulename, manualentries),
                    SwiftModuleScanner(modulename),
                    KSSPrereqsScanner(modulename)
                    ]
        for scanner in scanners:
            scanner.add_licenses(licenses)
        _write_licenses(outputfile, licenses, _generated_metadata())
    finally:
        os.chdir(cwd)

if __name__ == '__main__':
    scan()
