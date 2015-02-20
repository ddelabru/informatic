# Copyright 2015 Dominic Delabruere
#
# This Makefile is written for the developer's convenience. It will only work
# on Debian systems with certain tools installed.

ts:
	pylupdate5 -noobsolete informatic.pro

qm:
	lrelease informatic.pro

rc: qm
	pyrcc5 informatic/rc.qrc > informatic/rc.py

clean:
	rm -rf *.tar.gz *.egg-info dist deb_dist informatic/__pycache__
	rm -f informatic/rc.py informatic/*.qm

sdist:
	python3 setup.py sdist

deb:
	python3 setup.py --command-packages=stdeb.command bdist_deb

all: clean rc sdist deb

.PHONY: ts lrelease rc clean sdist deb all