PREFIX := kss

include BuildSystem/python/common.mk

check: build
	python3 -m unittest discover --start-directory Tests/unit
	behave Tests/features
