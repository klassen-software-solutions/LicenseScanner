"""GitHub API for looking up licenses"""

import logging
import urllib.parse

from typing import List

import kss.util.jsonreader as jsonreader


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
        if project.endswith('.git'):
            project = project[:-4]
        if organization in self._cached:
            return self._license_from_entry(self._cached[organization], project)
        if host == 'github.com':
            logging.info("   Looking up '%s' in github", url)
            projects = self._try_api('orgs', organization)
            if projects is None:
                projects = self._try_api('users', organization)
            if projects is not None:
                self._cached[organization] = projects
                return self._license_from_entry(projects, project)
        return None

    def _try_api(self, key: str, organization: str) -> List:
        if self._can_call_github():
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

    def _can_call_github(self) -> bool:
        try:
            if self._remaining_calls == -1:
                result = jsonreader.from_url("https://api.github.com/rate_limit")
                self._remaining_calls = result['rate']['remaining']
            logging.debug("  GitHub API calls remaining: %d", self._remaining_calls)
            if self._remaining_calls > 0:
                self._remaining_calls -= 1
                return True
            return False
        # pylint: disable=broad-except
        #   Justification: We really do want to trap all non-system-exiting exceptions.
        except Exception as ex:
            logging.warning("%s", ex)
            return False

    @classmethod
    def _license_from_entry(cls, projects: List, project_name: str) -> str:
        for project in projects:
            if project.get('name', '') == project_name:
                lic = project.get('license', {})
                lic_name = lic.get('spdx_id', None)
                if lic_name:
                    logging.debug("  Github identified license as '%s'", lic_name)
                return lic_name
        return None
