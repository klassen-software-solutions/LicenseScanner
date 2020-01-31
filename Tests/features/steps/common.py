import os

from behave import given, when, then, step
from kss.license import scanner

@when(u'we scan the "{project}" project')
def step_impl(context, project):
    directory = "Tests/Projects/%s" % project
    if not os.path.isdir(directory):
        raise FileNotFoundError(directory)
    scanner.scan(["--directory=%s" % directory, "--verbose"])
