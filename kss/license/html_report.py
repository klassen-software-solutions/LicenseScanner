#!/usr/bin/env python3

"""Takes a licenses JSON file and writes out an HTML report."""

import argparse
import base64
import html
import logging
import pkgutil

from typing import Dict, List

import kss.util.jsonreader as jsonreader

from .util import SPDX


def _read_licenses(filename: str) -> List:
    logging.info("Reading licenses from '%s'", filename)
    data = jsonreader.from_file(filename)
    if "dependencies" not in data:
        raise TypeError("%s should contain a dependencies item" % filename)
    licenses = data['dependencies']
    if not isinstance(licenses, List):
        raise TypeError("%s: dependencies should contain a JSON list" % filename)
    return licenses

def _write_licenses(licenses: Dict, local_license_filename: str, filename: str):
    spdx = SPDX()
    logging.info("Writing HTML to '%s'", filename)
    with open(filename, 'w') as outfile:
        outfile.write("<!DOCTYPE html>\n")
        outfile.write("<!-- Auto-generated by kss.license.html_report. Do not edit manually. -->\n")
        outfile.write("<html>\n")
        outfile.write("<head>\n")
        outfile.write("<style>\n")
        outfile.write(pkgutil.get_data(__name__, 'resources/_styles.css').decode('utf-8'))
        outfile.write("</style\n")
        outfile.write("</head>\n")
        outfile.write("<body>\n")
        _write_local_license(local_license_filename, outfile)
        outfile.write("<p>This project makes use of resources from the following third parties.\n")
        outfile.write("Their use is subject to the licenses described here.</p>\n")
        outfile.write("<ul id='topUL'>\n")
        for lic in licenses:
            _write_license(lic, spdx, outfile)
        outfile.write("</ul>\n")
        outfile.write("<script>\n")
        outfile.write(pkgutil.get_data(__name__, 'resources/_scripts.js').decode('utf-8'))
        outfile.write("</script>\n")
        outfile.write("</body>\n")
        outfile.write("</html>\n")

def _write_local_license(local_license_filename: str, outfile):
    if local_license_filename:
        with open(local_license_filename, 'r') as infile:
            outfile.write("<p>This software is subject to the following license agreement.</p>\n")
            outfile.write("<ul id='licenseUL'>\n")
            outfile.write("  <li><span class='caret'>View License</span>\n")
            outfile.write("  <ul class='nested lictext boxed'>")
            outfile.write("  <li>%s</li>\n" % infile.read())
            outfile.write("  </ul>\n")
            outfile.write("  </li>\n")
            outfile.write("</ul>\n")

def _write_license(lic: Dict, spdx, outfile):
    name = lic.get('moduleName', '')
    logging.info("  module: %s", name)
    outfile.write("<!-- %s -->\n" % html.escape(name))
    outfile.write("  <li><span class='caret'>%s</span>\n" % html.escape(name))
    outfile.write("  <ul class='nested boxed'>\n")
    url = lic.get('moduleUrl', None)
    if url:
        outfile.write("  <li>Project URL: <a href='%s'>%s</a></li>\n" % (url, html.escape(url)))
    _write_license_details(lic, spdx, outfile)
    outfile.write("  </ul>\n")
    outfile.write("  </li>\n")

def _write_license_details(lic: Dict, spdx, outfile):
    name = lic.get('moduleLicense', None)
    if name:
        outfile.write("  <li>License: %s\n" % html.escape(name))
        _write_license_text(lic, outfile)
        spdxid = lic.get('x-spdxId', None)
        if spdxid:
            _write_spdx_info(spdx.get_entry(spdxid), outfile)

def _write_license_text(lic: Dict, outfile):
    textencoded = lic.get('x-licenseTextEncoded', None)
    if textencoded:
        text = base64.b64decode(textencoded).decode('utf-8')
        outfile.write("  <li><span class='caret'>License Text</span>\n")
        outfile.write("  <ul class='nested lictext'>")
        outfile.write("  <li>%s</li>\n" % text)
        outfile.write("  </ul>\n")
        outfile.write("  </li>\n")

def _write_spdx_info(entry: Dict, outfile):
    if entry:
        seealso = entry.get('seeAlso', None)
        if seealso:
            outfile.write("  <li>See Also:\n")
            outfile.write("  <ul class='licdetails'>\n")
            for url in seealso:
                outfile.write("   <li><a href='%s'>%s</a></li>\n"
                              % (url, html.escape(url)))
            outfile.write("  </ul>\n")
            outfile.write("  </li>\n")


def _parse_command_line(args: List):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true', help='Show debugging information')
    parser.add_argument('--input',
                        default='Dependencies/prereqs-licenses.json',
                        help='Input licenses JSON file. (Default is '
                        + '"Dependencies/prereqs-licenses.json")')
    parser.add_argument('--local-license', help='License file for the local project (optional)')
    parser.add_argument('--output', help='Output HTML file', required=True)
    return parser.parse_args(args)

def generate_report(args: List = None):
    """Main entry point for the html reporter."

    Parameters:
        args: list of strings specifying the arguments. If none then sys.argv will be used.
    """
    options = _parse_command_line(args)
    logging.getLogger().setLevel(logging.DEBUG if options.verbose else logging.INFO)
    _write_licenses(_read_licenses(options.input), options.local_license, options.output)

if __name__ == '__main__':
    generate_report()
