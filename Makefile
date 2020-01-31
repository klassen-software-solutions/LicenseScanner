.PHONY: analyze build check clean

build:

check: build
	behave Tests/features

analyze:
	pylint kss
	
clean:
	rm -rf *~
	find . -name "__pycache__" -type d -exec rm -r "{}" \;
