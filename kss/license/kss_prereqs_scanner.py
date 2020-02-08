"""Scanner that handles dependencies of the form used by the KSS BuildSystem."""

import logging
import os
import urllib.parse
from operator import itemgetter
from typing import Dict, List, Tuple

import kss.util.command as command
import kss.util.jsonreader as jsonreader
from kss.util.strings import remove_suffix

from .directory_scanner import DirectoryScanner
from .util import find_all


class KSSPrereqsScanner(DirectoryScanner):
    """Scanner that searches the KSS BuildSystem prerequisites file.

    Specifically this looks for files of the form "prereqs.json" and
    attempts to identify the licenses of the given projects.
    """

    def __init__(self, modulename: str):
        super().__init__(modulename)
        self._prereqs = None
        self._pips = []
        self._osdir = "%s-%s" % (command.get_run("uname -s"), command.get_run("uname -m"))

    def should_scan(self) -> bool:
        self._prereqs = find_all("prereqs.json", skipprefix="Tests/")
        return bool(self._prereqs)

    def get_project_list(self) -> List:
        assert self._prereqs is not None, "Guaranteed by return of should_scan()"
        projects = []
        if self._prereqs:
            for filename in self._prereqs:
                logging.info("   searching '%s'", filename)
                entries, pips = self._get_projects_for_prereqs_file(filename)
                if entries:
                    entries.sort(key=itemgetter('name'))
                    logging.info("      found %s", [sub['name'] for sub in entries])
                    projects.extend(entries)
                if pips:
                    pips.sort()
                    logging.info("      found %s", pips)
                    self._pips.extend(pips)
        return projects

    def pre_project_callback(self, project: Dict) -> List:
        newlicenses = self._get_existing_prereqs_for_project(project)
        if newlicenses:
            logging.info("      also found %s", sorted([sub['moduleName'] for sub in newlicenses]))
        return newlicenses

    def scan(self) -> List:
        licenses = []
        licenses.extend(super().scan())
        licenses.extend(self._get_pip_licenses())
        return licenses

    def _add_directory_base_licenses(self, licenses: Dict):
        lics = super().scan()
        for lic in lics:
            licenses[lic['moduleName']] = lic

    def _get_projects_for_prereqs_file(self, filename: str) -> (List, List):
        entries = []
        pips = []
        for prereq in jsonreader.from_file(filename):
            if 'git' in prereq:
                entries.append(self._get_entry_from_git_prereq(prereq))
            elif 'tarball' in prereq:
                entries.append(self._get_entry_from_tarball_prereq(prereq))
            elif 'pip' in prereq:
                pips.append(prereq['pip'])
        return (entries, pips)

    def _get_entry_from_git_prereq(self, entry: Dict) -> Dict:
        assert 'git' in entry, "Guaranteed by _get_projects_for_prereqs_file()"
        url = entry['git']
        name = remove_suffix(os.path.basename(urllib.parse.urlparse(url).path), '.git')
        directory = self._find_path_for_project_directory(name)
        version = None
        filename = "%s/REVISION" % directory
        if os.path.isfile(filename):
            version = self._read_file_contents(filename)
        return {'name': name, 'version': version, 'directory': directory, 'url': url}

    def _get_entry_from_tarball_prereq(self, entry: Dict) -> Dict:
        assert 'tarball' in entry, "Guaranteed by _get_projects_for_prereqs_file()"
        url = entry['tarball']
        filename = entry.get('filename', None)
        if not filename:
            filename = os.path.basename(urllib.parse.urlparse(url).path)
        (name, version, directory) = self._parse_tarball_name(filename)
        return {'name': name, 'version': version, 'directory': directory, 'url': url}

    def _parse_tarball_name(self, filename: str) -> Tuple:
        name = remove_suffix(filename, '.tar.gz')
        directory = self._find_path_for_project_directory(name)
        parts = name.split('-', 1)
        name = parts[0]
        version = None if len(parts) == 1 else parts[1]
        return (name, version, directory)

    def _find_path_for_project_directory(self, dirname: str) -> str:
        for prereqdir in find_all(".prereqs", isdir=True):
            pathname = "%s/%s/%s" % (prereqdir, self._osdir, dirname)
            if os.path.isdir(pathname):
                logging.debug("Found project in %s", pathname)
                return pathname
        return None

    def _get_pip_licenses(self) -> List:
        piplicenses = []
        if self._pips:
            for pip in self._pips:
                logging.info("   examining '%s'", pip)
                self._add_pip_license_for(pip, None, piplicenses)
        return piplicenses

    def _add_pip_license_for(self, pip: str, used_by: str, licenses: List):
        lic = {'moduleName': pip}
        details = self._get_pip_module_details(pip)
        if not details:
            lic['moduleLicense'] = 'Unknown'
        else:
            requires = details.get('Requires', [])
            if requires:
                logging.info("      %s: also found %s", pip, requires)
                for req in requires:
                    self._add_pip_license_for(req, pip, licenses)
            licensetype = details.get('License', None)
            if not licensetype:
                licensetype = self._guess_pip_license_using_ninka(details)
            if not licensetype:
                licensetype = 'Unknown'
            lic['moduleLicense'] = licensetype
            lic['moduleVersion'] = details.get('Version', None)
            lic['moduleUrl'] = details.get('Home-page', None)
        if used_by:
            self.ensure_used_by(used_by, lic)
        licenses.append(lic)

    @classmethod
    def _get_existing_prereqs_for_project(cls, project: Dict) -> List:
        directory = project.get('directory', None)
        if directory:
            filename = "%s/Dependencies/prereqs-licenses.json" % directory
            if os.path.isfile(filename):
                return jsonreader.from_file(filename)['dependencies']
        return None

    @classmethod
    def _read_file_contents(cls, filename: str) -> str:
        with open(filename, 'r') as file:
            data = file.read().replace('\n', '')
        return data.strip()

    @classmethod
    def _get_pip_module_details(cls, pip: str) -> Dict:
        details = {}
        for line in command.process("python3 -m pip show %s" % pip):
            detail = line.split(':', 1)
            assert len(detail) > 0, 'it should not be possible to get nothing here'
            key = detail[0]
            value = None
            if len(detail) > 1:
                value = detail[1].strip()
                if value == '':
                    value = None
                if key == 'Requires' and value is not None:
                    value = [x.strip() for x in value.split(',')]
            if value is not None:
                details[key] = value
        return details

    @classmethod
    def _guess_pip_license_using_ninka(cls, pipdetails: Dict) -> str:
        location = pipdetails.get('Location', None)
        version = pipdetails.get('Version', None)
        pipname = pipdetails.get('Name', None)
        if location and version and pipname:
            dirname = "%s/%s-%s.dist-info" % (location, pipname, version)
            licensetype = cls.ninka.guess_license(dirname)
            if licensetype == 'Unknown':
                dirname = "%s/%s-%s.dist-info" % (location, pipname.replace('-', '_'), version)
                licensetype = cls.ninka.guess_license(dirname)
            return licensetype
        return None
