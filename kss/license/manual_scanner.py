"""Scanner that adds manually specified licenses."""

import logging
import os
from typing import List

import kss.util.jsonreader as jsonreader

from .scanner import Scanner


class ManualScanner(Scanner):
    """Scanner that adds any existing items that have been manually edited."""

    def __init__(self, filename: str):
        super().__init__()
        self._filename = filename

    def should_scan(self) -> bool:
        return os.path.isfile(self._filename)

    def scan(self) -> List:
        entries = jsonreader.from_file(self._filename)
        if not isinstance(entries, list):
            raise TypeError("%s should contain a JSON list" % self._filename)
        logging.info("   found %s", [sub['moduleName'] for sub in entries])
        return entries
