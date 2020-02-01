import os
from typing import Dict, List

from behave import given, when, then, step

import kss.util.jsonreader as jsonreader
from kss.license import entry_point


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
    entry_point.scan(["--directory=%s" % directory])
    context.project = project


# MARK: Thens

@then(u'there should be no output file')
def step_impl(context):
    filename = "Tests/Projects/%s/Dependencies/prereqs-licenses.json" % context.project
    assert not os.path.isfile(filename), "%s should not exist" % filename
    context.licenses = None

@then(u'there should be an output file')
def step_impl(context):
    filename = "Tests/Projects/%s/Dependencies/prereqs-licenses.json" % context.project
    assert os.path.isfile(filename), "%s should exist" % filename
    context.licenses = jsonreader.from_file(filename)

@then(u'there should be {count:d} modules')
def step_impl(context, count):
    assert len(context.licenses['dependencies']) == count, "Should have %d entries" % count

@then(u'module "{module}" should have a "{license}" license with a "{spdx}" spdx entry')
def step_impl(context, module, license, spdx):
    license = _unescape(license)
    entry = _find_entry(module, context.licenses)
    assert entry is not None, "Module %s should have an entry" % module
    assert entry['moduleLicense'] == license, "Module %s should be a %s license" % (module, license)
    assert entry['x-spdxId'] == spdx, "Module %s should have %s spdx id" % (module, spdx)
