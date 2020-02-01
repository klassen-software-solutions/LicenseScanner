"""SPDX database access"""

import json
import logging
import pkgutil

from typing import Dict


class SPDX:
    """Utility class used to access the SPDX database."""

    # The Ninka fallbacks contain a number of results we have received from Ninka that
    # represent valid entries, but do not quite label then properly.
    _ninka_fallbacks = {
        'spdxBSD3': 'BSD-3-Clause',
        'Apache-2': 'Apache-2.0'
    }

    _licenses = None
    _namemap = None

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
        Otherwise, if srch is a valid license name, we return that result,
        Otherwise, if srch is one of our known Ninka fallbacks, we return that result,
        Otherwise we return None.
        """
        entry = self.get_entry(srch)
        if not entry:
            entry = self._try_name_search(srch)
            if not entry:
                entry = self._try_ninka_overrides(srch)
        if entry:
            logging.debug("  SPDX identified '%s' as '%s' (id='%s')",
                          srch,
                          entry['name'],
                          entry['licenseId'])
        return entry

    def _try_name_search(self, name: str) -> Dict:
        licenseid = self._namemap.get(name, None)
        if licenseid:
            return self.get_entry(licenseid)
        return None

    def _try_ninka_overrides(self, name: str) -> Dict:
        licenseid = self._ninka_fallbacks.get(name, None)
        if licenseid:
            return self.get_entry(licenseid)
        if name.startswith('spdx'):
            return self.get_entry(name[4:])
        return None
