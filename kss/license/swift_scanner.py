"""Scanner that handles dependencies from Swift Xcode modules."""

import logging
import os
from operator import itemgetter

import kss.util.command as command
import kss.util.jsonreader as jsonreader

from .directory_scanner import DirectoryScanner
from .util import find_all


class SwiftModuleScanner(DirectoryScanner):
    """Scanner that searches for Swift modules

    Specifically this searches for `Package.resolved` files and examines the modules
    listed in them.

    Note that this scanner will look for the checked out modules in the directory
        `~/Library/Developer/Xcode/DerivedData`
    This directory can be changed by setting the environment variable
        `LICENSE_SCANNER_XCODE_DERIVED_DATA`
    but that should be rare other than for testing purposes.

    Also note that if there are multiple copies of a module checked out (which is likely
    if the developer has multiple Xcode projects that use the library), then the first
    match will be used for licensing purposes. This seems reasonable as it would be
    rare for the license to change often. If this is considered risky, it can be
    mitigated by cleaning out the DerivedData cache before building your project.
    """

    def __init__(self, modulename: str):
        super().__init__(modulename)
        self._files = None
        self._xcode_derived_data_directory = os.environ.get('LICENSE_SCANNER_XCODE_DERIVED_DATA',
                                                            '~/Library/Developer/Xcode/DerivedData')

    def should_scan(self) -> bool:
        self._files = self._get_xcode_package_dependency_files()
        return bool(self._files)

    def get_project_list(self) -> list:
        assert self._files is not None, "Guaranteed by return of should_scan()"
        projects = []
        for filename in self._files:
            logging.info("   searching '%s'", filename)
            entries = self._get_entries_for_xcode_package_dependency_file(filename)
            if entries:
                entries.sort(key=itemgetter('name'))
                logging.info("      found %s", [sub['name'] for sub in entries])
                projects.extend(entries)
        return projects

    @classmethod
    def _get_xcode_package_dependency_files(cls) -> list:
        return find_all('Package.resolved', skipprefix="Tests/")

    def _get_entries_for_xcode_package_dependency_file(self, filename: str) -> list:
        entries = []
        for pin in jsonreader.from_file(filename)['object']['pins']:
            name = pin['package']
            entry = {
                'name': name,
                'version': pin['state'].get('version', None),
                'directory': self._get_project_directory(name),
                'url': pin.get('repositoryURL', None)
            }
            entries.append(entry)
        return entries

    def _get_project_directory(self, name: str) -> str:
        deriveddata = os.path.expanduser(self._xcode_derived_data_directory)
        if os.path.isdir(deriveddata):
            for line in command.process("find %s -type d -name %s" % (deriveddata, name)):
                if os.path.isdir(line):
                    return line
        logging.warning("Could not find '%s' inside '%s'", name, deriveddata)
        return None
