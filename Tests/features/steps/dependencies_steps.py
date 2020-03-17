import os
from typing import Dict, List

from behave import given, when, then, step

import kss.util.jsonreader as jsonreader
from kss.license import entry_point, html_report


# MARK: Internal Utilities

def _find_entry(module: str, inLicenses: Dict) -> Dict:
    for entry in inLicenses['dependencies']:
        if entry['moduleName'] == module:
            return entry
    return None

def _unescape(s: str) -> str:
    return s.replace('\\"', '"')


# MARK: Whens

@when(u'we scan the "{project}" project')
def step_impl(context, project):
    directory = "Tests/Projects/%s" % project
    if not os.path.isdir(directory):
        raise FileNotFoundError(directory)
    entry_point.scan(["--directory=%s" % directory,
                      "--output=Dependencies/tmp-prereqs-licenses.json"])
    context.project = project

@when(u'we generate an HTML report')
def step_impl(context):
    directory = "Tests/Projects/%s" % context.project
    licfile = "%s/DUMMY_LICENSE.txt" % directory
    prereqsfile = "%s/Dependencies/tmp-prereqs-licenses.json" % directory
    htmlfile = "%s/t.html" % directory
    context.htmlfile = htmlfile
    html_report.generate_report(["--input=%s" % prereqsfile,
                                 "--local-license=%s" % licfile,
                                 "--output=%s" % htmlfile])


# MARK: Thens

@then(u'there should be no output file')
def step_impl(context):
    filename = "Tests/Projects/%s/Dependencies/tmp-prereqs-licenses.json" % context.project
    assert not os.path.isfile(filename), "%s should not exist" % filename
    context.licenses = None

@then(u'there should be an output file')
def step_impl(context):
    filename = "Tests/Projects/%s/Dependencies/tmp-prereqs-licenses.json" % context.project
    assert os.path.isfile(filename), "%s should exist" % filename
    context.licenses = jsonreader.from_file(filename)
    metadata = context.licenses.get('generated', None)
    assert metadata is not None
    assert metadata.get('process', None) is not None
    assert metadata.get('project', None) is not None
    assert metadata.get('time', None) is not None

@then(u'there should be {count:d} modules')
def step_impl(context, count):
    found = len(context.licenses['dependencies'])
    assert found == count, "Should have %d entries, found %d" % (count, found)

@then(u'the project should be used by {count:d} modules')
def step_impl(context, count):
    matches = 0
    for entry in context.licenses['dependencies']:
        if context.project in entry.get('x-usedBy', []):
            matches += 1
    assert matches == count, "%d entries should have '%s' in the x-usedBy field" % (count, context.project)

@then(u'module "{module}" should be "{license}" with a "{spdx}" spdx id')
def step_impl(context, module, license, spdx):
    license = _unescape(license)
    entry = _find_entry(module, context.licenses)
    assert entry is not None, "Module %s should have an entry" % module
    assert entry['moduleLicense'] == license, "Module %s should be a %s" % (module, license)
    assert entry['x-spdxId'] == spdx, "Module %s should have %s spdx id" % (module, spdx)

@then(u'module "{module}" should be "{license}" with no spdx id')
def step_impl(context, module, license):
    license = _unescape(license)
    entry = _find_entry(module, context.licenses)
    assert entry is not None, "Module %s should have an entry" % module
    assert entry['moduleLicense'] == license, "Module %s should be a %s" % (module, license)
    assert 'x-spdxId' not in entry, "Module %s should not have an spdx id" % module

@then(u'there should be an HTML report')
def step_impl(context):
    assert os.path.isfile(context.htmlfile), "HTML report %s should exist" % context.htmlfile

@then(u'the HTML report should include an entry for each license')
def step_impl(context):
    with open(context.htmlfile, "r") as infile:
        data = infile.read()
        for lic in context.licenses['dependencies']:
            print("!! lic: %s" % lic)
            name = lic['moduleName']
            str = "<li><span class='caret'>%s</span>" % name
            assert data.find(str) != -1, "Module %s should be in the report" % name
