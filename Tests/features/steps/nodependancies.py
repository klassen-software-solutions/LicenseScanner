import os

from behave import given, when, then, step

@then(u'"{project}" will not contain an output file')
def step_impl(context, project):
    filename = "Tests/Projects/%s/Dependencies/prereqs-licenses.json" % project
    assert not os.path.isfile(filename), "%s should not exist" % filename
