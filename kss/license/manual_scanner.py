"""Scanner that adds manually specified licenses."""

import logging
from typing import List

import kss.util.jsonreader as jsonreader

from .scanner import Scanner
from .util import find_all


class ManualScanner(Scanner):
    """Scanner that adds any existing items that have been manually edited."""

    def __init__(self, modulename: str, filename: str):
        super().__init__(modulename)
        self._filename = filename
        self._filenames = None

    def should_scan(self) -> bool:
        self._filenames = find_all(self._filename, skipprefix="Tests/")
        return bool(self._filenames)

    def scan(self) -> List:
        entries = []
        for filename in self._filenames:
            logging.info("   searching '%s'", filename)
            newentries = jsonreader.from_file(filename)
            if not isinstance(newentries, List):
                raise TypeError("%s should contain a JSON list" % filename)
            logging.info("      found %s", [sub['moduleName'] for sub in newentries])
            entries.extend(newentries)
        return entries
