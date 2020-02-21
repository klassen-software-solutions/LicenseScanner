# LicenseScanner
Utility for scanning a project to determine the licenses used by its dependencies.

## Prerequisites

* Python 3.7+
* Behave (can be installed by running `python3 -m pip install behave`)
* Ninka (can be installed by running `./install-ninka.sh /usr/local`)
* kss-pyutil (can be installed by running `python3 -m pip install kss-pyutil` or `make install`)
* pylint (can be installed by running `python3 -m pip install pylint`)

## Format of the Output License File

The license file we create is a JSON file based on the one defined in the GitHub project
'jk1/Gradle-License-Report', but with a few additional fields.

The main fields that we populate are as follows:

* `moduleName`: The name of the prerequisite module.
* `moduleVersion`: (Optional) The version of the module if it can be determined.
* `moduleLicense`: The name of the license used or `Unknown` if it could not be determined.
* `moduleUrl`: (Optional) Identifies the source of the module if it can be determined.

In addition, we add the following fields:

* `x-usedBy`: Will list all the prerequisites that use this module.
* `x-spdxId`: (Optional) Set if the license can be identified in the SPDX database.
* `x-isOsiApproved`: (Optional) Set to `true` if SPDX identifies this license type as OSI approved.
* `x-licenseTextEncoded`: (Optional) Full text of the license, base64 encoded.

## Commands for Developing

* `git submodule update --init --recursive` is needed after checking out to update the build system
* `make` will perform a local build
* `make install` will install the local build and its dependencies
* `make check` will run all the tests
* `make analyze` will run a static analysis (currently just `pylint`) on the code

## Testing

There are two types of automated testing in this project. Unit tests are used to test various utility
methods and are created by adding them in `Tests/unit`. BDD tests are used to test the overall
operation and are added by modifying `Tests/features/dependencies.feature`.

When a new type of scanner is added, a new test project should be added to `Tests/Projects` and
a new scenario should be added to the BDD tests. This should ensure that the new scanner will work
on a simple project of that type. 

In addition, a new subproject should be added to `Tests/Projects/MultiProject` and the
multi-project scenarious should be updated, to ensure that the new scanner will also work on
projects that are a part of a larger one.

## Coding Standards and Procedures

If you are going to contribute to this project, please make yourself familiar with the following
standards and procedures.

* [Git Procedures](https://www.kss.cc/standards-git.html)
* [Python Coding Standards](https://www.kss.cc/standards-python.html)

_One note on the CI_: For some reason the macOS GitHub VMs always report that no GitHub API calls
are available, causing the behave tests to fail. As a result we only run the CI on the Linux VMs. Any changes
you create are still required to work on the mac, but the testing must be done on a development machine
and not in the CI.
