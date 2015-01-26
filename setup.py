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
    entry_points = {
        'gui_scripts': [
            'informatic = informatic.mainwin:main'
            ],
        },
    author = 'Dominic Delabruere',
    author_email = 'dominic.delabruere@gmail.com',
    description = 'Informatic is an IDE for the Inform 6 language.',
    license = 'GPL',
    keywords = 'inform inform6 ide', 
    classifiers = ['Development Status :: 3 - Alpha',
    'Environment :: X11 Applications :: Qt',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Text Editors :: Integrated Development Environments (IDE)']
    )

# If the /usr/share/applications directory exists, the Informatic shortcut is
# copied into it upon installation.
if os.path.isdir('/usr/share/applications'):
    setup_options['data_files'] = [
        ('/usr/share/applications/',
            ['informatic.desktop']
            )
        ]

# Test whether PyQt5 and PyQt5.Qsci are installed. They can't be mentioned as
# requirements in the setup() parameters because setuptools can't install them.
qsciImported = False
try:
    import PyQt5.QtWidgets
    widgetsImported = True
    del PyQt5.QtWidgets
except:
    widgetsImported = False
    print('Python failed to import from PyQt5. Make sure PyQt5 is installed.')

try:
    import PyQt5.Qsci
    qsciImported = True
    del PyQt5.Qsci
except:
    qsciImported = False
    print('Python failed to import the Qscintilla plugin for PyQt5 '
    '(PyQt5.Qsci).\nMake sure it is installed.')

# The script will not run setup() unless PyQt5 and PyQt5.Qsci are present
if widgetsImported and qsciImported:
    setup(**setup_options)
else:
    print('Missing dependencies; aborting...')
