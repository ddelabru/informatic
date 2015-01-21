#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

setup(name='informatic', 
    version='0.1',
    description='Inform 6 IDE',
    options={'build_exe': {'includes': ['atexit', 'PyQt5.QtPrintSupport'],
        'include_msvcr': True}},
    executables=[Executable('informatic.pyw', base=base)]
    )
