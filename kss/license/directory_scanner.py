"""Base class for scanners that search existing source code checkouts."""

import logging

from abc import abstractmethod
import os
from typing import Dict, List

import kss.util.jsonreader as jsonreader

from .scanner import Scanner
from .util import read_encoded, Ninka


class DirectoryScanner(Scanner):
    """Base class that can be used for scanners that examine checked out source code.

    This can be subclassed to create a scanner that will search for licenses in an
    existing code based. The subclass will define what directories should be examined
    by overriding the `get_project_list()` method.
    """

    ninka = Ninka()

    def __init__(self, modulename: str):
        super().__init__(modulename)
        self._entries = None

    def scan(self) -> List:
        lics = []
        entries = self.get_project_list()
        for prereq in entries:
            logging.info("   examining '%s'", prereq['name'])
            lics.extend(self.pre_project_callback(prereq) or [])
            lics.extend(self._get_existing_prereqs_for_project(prereq) or [])
            lics.append(self._process_prereq(prereq))
        return lics

    @abstractmethod
    def get_project_list(self) -> List:
        """Subclasses must override this to return a list of dictionary objects.

        Each object in the returned list should have the following members:
          name: a string containing the project name
          directory: a string providing where the directory exists
          version (optional): a string containing the project version
          url (optional): a string providing the project URL
        """
        raise NotImplementedError()

    # pylint: disable=no-self-use
    #   Justification: self is required as part of the API.
    def pre_project_callback(self, _project: Dict) -> List:
        """Subclasses may override this to perform work for a given project.

        This method will be called by the `scan()` method just before it
        processes each project. Subclasses may override this in order to perform
        any custom work that should be done at that time and to return any
        additional licenses that should be recorded.

        Note that the returned list is a list of licenses, not a list of project
        entries.
        """
        return None

    @classmethod
    def _get_existing_prereqs_for_project(cls, project: Dict) -> List:
        directory = project.get('directory', None)
        if directory:
            filename = "%s/Dependencies/prereqs-licenses.json" % directory
            if os.path.isfile(filename):
                newlicenses = jsonreader.from_file(filename)['dependencies']
                logging.info("      also found %s",
                             sorted([sub['moduleName'] for sub in newlicenses]))
                return newlicenses
        return None

    @classmethod
    def _process_prereq(cls, prereq: Dict) -> Dict:
        details = cls._details_for_prereq(prereq)
        return cls._license_from_details(details)

    @classmethod
    def _details_for_prereq(cls, entry: Dict) -> Dict:
        details = entry.copy()
        directory = entry['directory']
        details['license'] = 'Unknown'
        if directory is not None and os.path.isdir(directory):
            (details['license'], details['license-filename']) = cls.ninka.guess_license(directory)
        return details

    @classmethod
    def _license_from_details(cls, details: Dict) -> Dict:
        lic = {'moduleName': details['name']}
        if details['version']:
            lic['moduleVersion'] = details['version']
        if details['url']:
            lic['moduleUrl'] = details['url']
        licensefilename = details.get('license-filename', None)
        if licensefilename:
            lic['x-licenseTextEncoded'] = read_encoded(licensefilename)
        lic['moduleLicense'] = 'Unknown' if not details['license'] else details['license']
        return lic
