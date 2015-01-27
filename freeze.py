#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

"""
This script is used for building standalone Windows executables of
Informatic, bundled with all the application's dependencies. cx_Freeze
invokes distutils, but for all installation and packaging tasks it is
recommended that you use the setup.py script instead.

Depending on the cx_Freeze version being used, one may have to copy
libEGL.dll by hand when building the Windows executable.
"""

import sys
from cx_Freeze import setup, Executable

from informatic import version

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

setup(name='informatic', 
    version=version,
    description='Inform 6 IDE',
    options={'build_exe': {'includes': ['atexit', 'PyQt5.QtPrintSupport'],
        'include_msvcr': True}},
    executables=[Executable('informatic.pyw', base=base)]
    )
