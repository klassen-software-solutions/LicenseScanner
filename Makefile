.PHONY: analyze build check clean

build:

check: build
	python3 -m unittest discover --start-directory Tests/unit
	behave Tests/features

analyze:
	pylint kss
	
clean:
	-rm -rf *~
	-find . -name "__pycache__" -type d -exec rm -r "{}" \;
