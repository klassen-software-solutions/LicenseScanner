# LicenseScanner
Utility for scanning a project to determine the licenses used by its dependencies.

## Prerequisites

* Python 3.7+
* Behave (can be installed by running `python3 -m pip install behave`)
* Ninka (can be installed by running `./install-ninka.sh /usr/local`)
* kss-pyutil (can be installed by running `python3 -m pip install kss-pyutil` or `make install`)
* pylint (can be installed by running `python3 -m pip install pylint`)

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

## Git Procedures

* The main development branch is currently `development/v1`. It should be your starting point.
* Your working branch should be of the form `feature/99-some-description` where `99` is referencing an issue number.
* When you checkin your branch the CI will automatically run the tests and the static analysis. You should have
done this manually before checking in to reduce the number of times that the CI fails.
* If you prefix your check with `WIP:` then the CI will assume it is a work in progress and will not run
the checks or the analysis. Do this when you are just trying to save your state and don't actually want
the CI to run.
* Before you merge your feature into the development branch, try to squash your commits to eliminate
large numbers of `WIP` checkins. But if this gives you grief, then don't bother. It is not the end of the
world if you cannot.
* Do not use fast-forward merging when merging into the development branch. We want to see the
create commit and the separate branch.
* Do not remove your branch when you are done. You can remove it locally, but we want to see it in the
repository as it helps trace problems.
* When your check has been merged into the development branch, you are essentially done with the issue.
The development branch will not be merged into the master branch until we are ready to create the
next release.

_One note on the CI_: For some reason the macOS GitHub VMs always report that no GitHub API calls
are available, causing the behave tests to fail. As a result we only run the CI on the Linux VMs. Any changes
you create are still required to work on the mac, but the testing must be done on a development machine
and not in the CI.
