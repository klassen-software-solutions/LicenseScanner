"""API for the scanning architecture."""

import bisect
import logging

from abc import ABC, abstractmethod

from .util import GitHub, SPDX


class Scanner(ABC):
    """Base class defining the scanning API."""

    _spdx = SPDX()
    _github = GitHub()
    _ignored = set()

    def __init__(self, modulename: str):
        self.modulename = modulename

    @abstractmethod
    def should_scan(self) -> bool:
        """Subclasses must override this to return True if this scanner is suitable for
           the current project. You may also assume that if it returns True then scan()
           will be called, and you can safely save any state needed by should_scan() to be
           reused by scan().
        """
        raise NotImplementedError()

    @abstractmethod
    def scan(self) -> list:
        """Subclasses must override this to return a list of license entries that should
           be recorded for the current project. You may assume that should_scan() has been
           called and has returned True.
        """
        raise NotImplementedError()

    def add_licenses(self, licenses: dict):
        """Calls should_scan() and scan() and adds the results to licenses."""
        if self.should_scan():
            logging.info("Running the scanner '%s'", type(self).__name__)
            new_licenses = self.scan()
            self._adjust_and_add_new_licenses(new_licenses, licenses)

    @classmethod
    def ensure_used_by(cls, usedby: str, lic: dict):
        """Ensure that usedby is in the x-usedBy list.

        Subclasses may use this if they need to manually add a usedby item. Typically
        this is done when processing a recursive system. Note that you do not need
        to call this to add the main module to the list as that will be handled
        automatically by this class.
        """
        if not usedby:
            raise ValueError('usedby value is missing')
        if 'x-usedBy' in lic:
            if usedby not in lic['x-usedBy']:
                bisect.insort(lic['x-usedBy'], usedby)
        else:
            lic['x-usedBy'] = [usedby]

    def _adjust_and_add_new_licenses(self, new_licenses: dict, licenses: dict):
        for lic in new_licenses:
            key = lic['moduleName']
            if key in self._ignored:
                logging.info("   Entry '%s' is already marked as ignored", lic['moduleName'])
            else:
                if lic.get('x-ignored', False):
                    self._ignored.add(key)
                    logging.info("   Ignoring '%s' by request", lic['moduleName'])
                else:
                    self._merge_or_add_license(lic, licenses)

    def _merge_or_add_license(self, lic: dict, licenses: dict):
        key = lic['moduleName']
        if key in licenses:
            self._merge_license(lic, licenses[key])
            logging.info("   Entry '%s' already exists", lic['moduleName'])
        else:
            self._resolve_details_and_add_license(lic, licenses)
            logging.info("   Added '%s' as '%s'",
                         lic['moduleName'],
                         lic['moduleLicense'])

    def _resolve_details_and_add_license(self, lic: dict, licenses: dict):
        if self._should_add_to_used_by(lic):
            self.ensure_used_by(self.modulename, lic)
        if 'moduleLicense' not in lic:
            lic['moduleLicense'] = 'Unknown'
        entry = self._spdx.search(lic.get('moduleLicense', None))
        if entry:
            self._set_spdx_info_into_license(entry, lic)
        else:
            licenseid = self._github.lookup(lic.get('moduleUrl', None))
            if licenseid:
                entry = self._spdx.get_entry(licenseid)
                if entry:
                    self._set_spdx_info_into_license(entry, lic)
        licenses[lic['moduleName']] = lic

    def _merge_license(self, source: dict, dest: dict):
        if source['moduleName'] != dest['moduleName']:
            raise ValueError('Can only merge licenses of the same module name.')
        if self._should_add_to_used_by(source):
            self.ensure_used_by(self.modulename, dest)
        for usedby in source.get('x-usedBy', []):
            self.ensure_used_by(usedby, dest)

    @classmethod
    def _set_spdx_info_into_license(cls, spdxentry: dict, lic: dict):
        lic['moduleLicense'] = spdxentry['name']
        lic['x-spdxId'] = spdxentry['licenseId']
        lic['x-isOsiApproved'] = spdxentry['isOsiApproved']

    @classmethod
    def _should_add_to_used_by(cls, lic: dict) -> bool:
        return 'x-usedBy' not in lic
