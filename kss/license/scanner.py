"""API for the scanning architecture."""

import bisect
import logging

from abc import ABC, abstractmethod
from typing import Dict, List

from .github import GitHub
from .spdx import SPDX


class Scanner(ABC):
    """Base class defining the scanning API."""

    _spdx = SPDX()
    _github = GitHub()

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
            self._adjust_and_add_new_licenses(modulename, new_licenses, licenses)

    def _adjust_and_add_new_licenses(self, modulename: str, new_licenses: Dict, licenses: Dict):
        for lic in new_licenses:
            key = lic['moduleName']
            if key in licenses:
                if self._should_add_to_used_by(lic):
                    self._ensure_used_by(modulename, licenses[key])
                logging.info("   Entry '%s' already exists", lic['moduleName'])
            else:
                if self._should_add_to_used_by(lic):
                    self._ensure_used_by(modulename, lic)
                self._resolve_details_and_add_license(lic, licenses)
                logging.info("   Added '%s' as '%s'",
                             lic['moduleName'],
                             lic['moduleLicense'])

    def _resolve_details_and_add_license(self, lic: Dict, licenses: Dict):
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

    @classmethod
    def _set_spdx_info_into_license(cls, spdxentry: Dict, lic: Dict):
        lic['moduleLicense'] = spdxentry['name']
        lic['x-spdxId'] = spdxentry['licenseId']
        lic['x-isOsiApproved'] = spdxentry['isOsiApproved']

    @classmethod
    def _should_add_to_used_by(cls, lic: Dict) -> bool:
        return 'x-usedBy' not in lic

    @classmethod
    def _ensure_used_by(cls, modulename: str, lic: Dict):
        if 'x-usedBy' in lic:
            if modulename not in lic['x-usedBy']:
                bisect.insort(lic['x-usedBy'], modulename)
        else:
            lic['x-usedBy'] = [modulename]
