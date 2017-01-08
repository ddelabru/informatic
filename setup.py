#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

"""
The setup script for informatic. Run this with the "install" command to install
Informatic on your system.
"""

# The version number is imported from the informatic package's __init__.py file.
from informatic import version

import os.path

# First try to use an existing setuptools installation. If that fails, attempt
# to download setuptools using the ez_setup script.
try:
    from setuptools import setup, find_packages
except:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

# setup() options are stored in a dictionary which can be altered before setup()
# is actually invoked.
setup_options = dict(
    name = 'informatic',
    version = version,
    packages = find_packages(),
    install_requires = ['PyQt5', 'QScintilla'],
    entry_points = {
        'gui_scripts': [
            'informatic = informatic.mainwin:main'
            ],
        },
    author = 'Dominic Delabruere',
    author_email = 'dominic.delabruere@gmail.com',
    description = 'IDE for the Inform 6 language',
    license = 'GPL',
    keywords = 'inform inform6 ide',
    url = 'http://github.com/mrloam/informatic',
    long_description = 'Informatic is an IDE for the Inform 6 interactive '
    'fiction development system.\nIt is written in Python 3, using PyQt5 for '
    'its GUI. Informatic does not come\nwith the Inform 6 compiler or '
    'libraries. These must be downloaded separately.\n',
    classifiers = ['Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Text Editors :: Integrated Development Environments (IDE)']
    )

# If the /usr/share/applications directory exists, the Informatic shortcut is
# copied into it upon installation, and the Informatic icon is copied into the
# appropriate directory.
if os.path.isdir('/usr/share/applications'):
    setup_options['data_files'] = [
        ('/usr/share/applications/',
            ['informatic.desktop']
            ),
        ('/usr/share/pixmaps/', 
            ['informatic/informatic.png'])
        ]

setup(**setup_options)
