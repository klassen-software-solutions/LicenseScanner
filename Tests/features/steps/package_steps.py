from behave import given, when, then, step
from kss.util import command

# MARK: Internal Utilities

def _find_file_match(pattern: str) -> str:
    files = []
    for line in command.process("find dist -name '%s'" % pattern):
        files.append(line)
    if len(files) == 0:
        raise RuntimeError("Could not find a dist file matching '%s'" % pattern)
    if len(files) > 1:
        raise RuntimeError("Found more than one dist file matching '%s'" % pattern)
    return files[0]

def _has_match(cmd: str, match: str) -> bool:
    for line in command.process(cmd):
        if line.find(match) != -1:
            return True
    return False


# MARK: Whens

@when(u'we build the installation packages')
def step_impl(context):
    pass


# MARK: Thens

@then(u'the source distribution should include the resources')
def step_impl(context):
    filename = _find_file_match("*.tar.gz")
    target = 'kss/license/resources/spdx-licenses.json'
    cmd = "tar tzf %s" % filename
    assert _has_match(cmd, target), "Should find '%s' in %s" % (target, filename)


@then(u'the binary distribution should include the resources')
def step_impl(context):
    filename = _find_file_match("*.whl")
    target = 'kss/license/resources/spdx-licenses.json'
    cmd = "unzip -l %s" % filename
    assert _has_match(cmd, target), "Should find '%s' in %s" % (target, filename)
