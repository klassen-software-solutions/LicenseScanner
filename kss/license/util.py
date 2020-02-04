"""Misc. utils used by the license package."""

import json
import logging
import os
import pkgutil
import urllib.parse

from typing import Dict, List

import kss.util.command as command
import kss.util.jsonreader as jsonreader
from kss.util.strings import remove_prefix, remove_suffix


def find_all(name: str, directory: str = ".", isdir: bool = False, skipprefix: str = None) -> List:
    """File tree walk search.

    This method starts at the given directory and performs a deep search for instances
    of the given file or directory. It returns a list of all the matches, relative to
    the starting directory.
    """
    matches = []
    for dirpath, dnames, fnames in os.walk(directory):
        if dirpath == directory:
            dirpath = ""
        dirpath = remove_prefix(dirpath, directory + "/")
        if dirpath.startswith("."):
            continue
        if skipprefix and dirpath.startswith(skipprefix):
            continue

        names = dnames if isdir else fnames
        if name in names:
            fullname = name if dirpath == "" else "%s/%s" % (dirpath, name)
            matches.append(fullname)
    return matches


class NotAvailableException(Exception):
    """Specifies that a resource is not available, but may be in the future."""


class Ninka:
    """Utility class used to guess a license given a directory."""

    @classmethod
    def guess_license(cls, dirname: str) -> str:
        """Given a directory, attempt to find a license file and identify it.

        This will always return a string, which will be 'Unknown' if the license
        could not be determined.
        """
        filename = cls._get_license_filename(dirname)
        if filename:
            return cls.guess_license_by_file(filename)
        return 'Unknown'

    @classmethod
    def guess_license_by_file(cls, filename: str) -> str:
        """Given a filename, attempt to identify the license type.

        This will always return a string, which will be 'Unknown' if the license
        could not be determined.
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)
        licensetype = command.get_run("ninka %s | cut -d ';' -f2" % filename)
        licensetype = remove_prefix(licensetype, 'spdx')
        logging.debug("Ninka identified license as '%s' based on %s",
                      licensetype,
                      filename)
        return licensetype


    @classmethod
    def _get_license_filename(cls, dirname: str):
        try:
            for entry in os.listdir(dirname):
                if entry.upper().startswith('LICENSE'):
                    return "%s/%s" % (dirname, entry)
        except FileNotFoundError:
            pass
        return None


class SPDX:
    """Utility class used to access the SPDX database."""

    _licenses = None
    _namemap = None

    # The following is a list of common license claims that are valid SPDX licenses,
    # but whose names are not exactly specified correctly.
    _name_fallbacks = {
        'BSD1': 'BSD-1-Clause',
        'BSD2': 'BSD-2-Clause',
        'BSD3': 'BSD-3-Clause',
        'BSD4': 'BSD-4-Clause',
        'Apache 2.0': 'Apache-2.0',
        'Apache-2': 'Apache-2.0'
    }

    def __init__(self):
        # Note that we are using a singleton pattern internally so that all copies of
        # SPDX are in fact using the same, readonly, data.
        if SPDX._licenses is None:
            logging.info("Reading SPDX data from resources/spdx-licenses.json")
            licenses = {}
            namemap = {}
            data = pkgutil.get_data(__name__, 'resources/spdx-licenses.json')
            for lic in json.loads(data)['licenses']:
                licenses[lic['licenseId']] = lic
                namemap[lic['name']] = lic['licenseId']
            SPDX._licenses = licenses
            SPDX._namemap = namemap

    def get_entry(self, licenseid: str) -> Dict:
        """Perform a direct search of the spdx id, returning None if it is not there."""
        return self._licenses.get(licenseid, None)

    def search(self, srch: str) -> Dict:
        """Search for an spdx entry.

        If srch is an spdx id, then we return the direct result,
        Otherwise, if srch is one of our commonly found fallbacks, we return that result,
        Otherwise, if srch is a valid license name, we return that result,
        Otherwise we return None.
        """
        entry = self.get_entry(srch)
        if srch in self._name_fallbacks:
            entry = self.get_entry(self._name_fallbacks[srch])
        if not entry:
            entry = self._try_name_search(srch)
        if entry:
            logging.debug("SPDX identified '%s' as '%s' (id='%s')",
                          srch,
                          entry['name'],
                          entry['licenseId'])
        return entry

    def _try_name_search(self, name: str) -> Dict:
        licenseid = self._namemap.get(name, None)
        if licenseid:
            return self.get_entry(licenseid)
        return None



# pylint: disable=too-few-public-methods
#   Justification: I do want this as a class to limit the scope of the global variables.
class GitHub:
    """Utility class that uses the GitHub API to try to determine a license."""

    _cached = {}
    _remaining_calls = -1

    # Note that we are using a singleton pattern internally so that all copies of GitHub
    # use the same cache and remaining call count. Note that this means the class is
    # not thread-safe, but that should be fine for our current scanner implementation.

    def lookup(self, url: str) -> str:
        """Lookup the project specified by the URL using the GitHub API.

        Returns the license name if it is found or None if it could not be determined.
        """
        host, organization, project = self._parse_url(url)
        if host == 'github.com':
            project = remove_suffix(project, '.git')
            if organization in self._cached:
                return self._license_from_entry(self._cached[organization], project)
            logging.debug("Looking up '%s' in github", url)
            projects = self._try_api('orgs', organization)
            if projects is None:
                projects = self._try_api('users', organization)
            if projects is not None:
                self._cached[organization] = projects
                return self._license_from_entry(projects, project)
        return None

    def _try_api(self, key: str, organization: str) -> List:
        self._ensure_can_call_github()
        try:
            return jsonreader.from_url("https://api.github.com/%s/%s/repos"
                                       % (key, organization))
        # pylint: disable=broad-except
        #   Justification: We really do want to trap all non-system-exiting exceptions.
        except Exception:
            pass
        return None

    @classmethod
    def _parse_url(cls, url):
        host = None
        organization = None
        project = None
        if url:
            parsed_url = urllib.parse.urlparse(url)
            host = parsed_url.netloc
            parts = parsed_url.path.split('/')
            for i, part in enumerate(parts):
                part = parts[i]
                if part == '':
                    continue
                if organization is None:
                    organization = part
                    continue
                if project is None:
                    project = part
                    break
        return host, organization, project

    def _ensure_can_call_github(self):
        allowable_calls = 0
        if self._remaining_calls == -1:
            result = jsonreader.from_url("https://api.github.com/rate_limit")
            self._remaining_calls = result['rate']['remaining']
            allowable_calls = result['rate']['limit']
        logging.debug("GitHub API calls remaining: %d of %d",
                      self._remaining_calls, allowable_calls)
        if self._remaining_calls > 0:
            self._remaining_calls -= 1
            return
        raise NotAvailableException("Out of GitHub API calls (%d allowed), try again later.",
                                    allowable_calls)

    @classmethod
    def _license_from_entry(cls, projects: List, project_name: str) -> str:
        for project in projects:
            if project.get('name', '') == project_name:
                lic = project.get('license', {})
                lic_name = lic.get('spdx_id', None)
                if lic_name:
                    logging.debug("Github identified license as '%s'", lic_name)
                return lic_name
        return None
