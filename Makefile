PREFIX := kss
PACKAGE := license

include BuildSystem/python/common.mk

check: build
	python3 -m unittest discover --start-directory Tests/unit
	env LICENSE_SCANNER_XCODE_DERIVED_DATA=`pwd`/Tests/Projects/FakeXcodeDerivedData \
		behave Tests/features
