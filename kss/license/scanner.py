#!/usr/bin/env python3

"""Scans a directory to determine the licenses of its dependancies."""

import argparse
import logging
import os
import pathlib
import sys

from abc import ABC, abstractmethod
from typing import Dict, List


# MARK: Scanner Infrastructure

class Scanner(ABC):
    """Base class defining the scanning API."""

    @abstractmethod
    def should_scan(self) -> bool:
        """Subclasses must override this to return True if this scanner is suitable for
           the current project. You may also assume that if it returns True then scan()
           will be called, and you can safely save any state needed by should_scan() to be
           reused by scan().
        """
        raise NotImplementedError()

    @abstractmethod
    def scan(self) -> List:
        """Subclasses must override this to return a List of license entries that should
           be recorded for the current project. You may assume that should_scan() has been
           called and has returned True.
        """
        raise NotImplementedError()

    def add_licenses(self, modulename: str, licenses: Dict):
        """Calls should_scan() and scan() and adds the results to licenses."""
        if self.should_scan():
            logging.info("Running the scanner '%s'", type(self).__name__)
            new_licenses = self.scan()
            #self._adjust_and_add_new_licenses(modulename, new_licenses, licenses)

#    def _adjust_and_add_new_licenses(self, modulename: str, new_licenses: Dict, licenses: Dict):
#        for lic in new_licenses:
#            key = lic['moduleName']
#            if key in licenses:
#                if self._should_add_to_used_by(lic):
#                    self._ensure_used_by(modulename, licenses[key])
#                logging.info("   Entry '%s' already exists", lic['moduleName'])
#            else:
#                if self._should_add_to_used_by(lic):
#                    self._ensure_used_by(modulename, lic)
#                self._resolve_details_and_add_license()
#                logging.info("   Added '%s' as '%s'",
#                             lic['moduleName'],
#                             lic['moduleLicense'])
#
#
#                entry = self.spdx.search(lic['moduleLicense'])
#                if entry:
#                    self.spdx.set_into_license(entry, lic)
#                else:
#                    licenseid = self._github.lookup(lic.get('moduleUrl', None))
#                    if licenseid:
#                        entry = self.spdx.get_entry(licenseid)
#                        if entry:
#                            self.spdx.set_into_license(entry, lic)
#                licenses[key] = lic
#                logging.info("   Added '%s' as '%s'",
#                             lic['moduleName'],
#                             lic['moduleLicense'])

#    def _resolve_details_and_add_license(self, lic: Dict, licenses: Dict):
#        entry = self.spdx.search(lic['moduleLicense'])
#        if entry:
#            self.spdx.set_into_license(entry, lic)
#        else:
#            licenseid = self._github.lookup(lic.get('moduleUrl', None))
#            if licenseid:
#                entry = self.spdx.get_entry(licenseid)
#                if entry:
#                    self.spdx.set_into_license(entry, lic)
#        licenses[key] = lic
#
#    @classmethod
#    def _should_add_to_used_by(cls, lic: Dict) -> bool:
#        return 'x-usedBy' not in lic
#
#    @classmethod
#    def _ensure_used_by(cls, modulename: str, lic: Dict):
#        if 'x-usedBy' in lic:
#            if modulename not in lic['x-usedBy']:
#                bisect.insort(lic['x-usedBy'], modulename)
#        else:
#            lic['x-usedBy'] = [modulename]



# MARK: Main entry point

def _parse_command_line(args: List):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true', help='Show debugging information')
    parser.add_argument('--directory',
                        default='.',
                        help='Directory to be scanned (defaults to the current working directory)')
    parser.add_argument('--name',
                        help='Name of module to be scanned (default is the basename of the '
                        + 'directory).')
    parser.add_argument('--output',
                        default='Dependencies/prereqs-licenses.json',
                        help='Output file, relative to the scanned directory. Default is '
                        + '"Dependencies/prereqs-licenses.json")')
    parser.add_argument('--manual-licenses',
                        default='Dependencies/manual-licenses.json',
                        metavar='FILENAME',
                        help='File containing manually generated license entries, relative to '
                        + 'the scanned directory. Default is "Dependencies/manual-licenses.json")')
    return parser.parse_args(args)


def _write_licenses(filename: str, licenses: Dict):
    if len(licenses) > 0:
        outputdir = os.path.dirname(outputfile)
        if outputdir:
            pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)
        data = {'dependencies': sorted(licenses.values(), key=lambda x: x['moduleName'])}
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
    else:
        logging.info("No dependencies found")


def scan(args: List = None):
    """Main entry point.

    Parameters:
        args: list of strings specifying the arguments. If None then sys.argv will be used.
    """

    options = _parse_command_line(args)
    logging.basicConfig(level=logging.DEBUG if options.verbose else logging.INFO)

    logging.debug("Options: %s", options)

    if not os.path.isdir(options.directory):
        raise FileNotFoundError(options.directory)

    directory = options.directory
    modulename = options.name or os.path.basename(os.getcwd())
    outputfile = options.output
    manualentries = options.manual_licenses

    logging.info("Scanning for licenses in '%s'", directory)
    logging.debug("  identifying module as '%s'", modulename)
    logging.debug("  will write output to '%s'", outputfile)
    logging.debug("  will look for manual entries in '%s'", manualentries)

    cwd = os.getcwd()
    try:
        os.chdir(directory)
        licenses = {}
        _write_licenses(outputfile, licenses)
    finally:
        os.chdir(cwd)

if __name__ == '__main__':
    scan()
