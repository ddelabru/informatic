#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

"""
The compiler module contains code for interfacing with the Inform 6 compiler.
"""

from PyQt5.QtCore import *
from subprocess import Popen, PIPE

from .project import Project

class Compiler(QThread):
    """
    The Compiler class, reimplemented from QThread, invokes the Inform compiler
    in a separate thread to avoid freezing the Informatic GUI while the compiler
    is running.
    """
    
    done = pyqtSignal(str)
    
    @pyqtSlot()
    def run(self):
        """
        Runs the compiler using options set in the constructor. Waits for the
        compiler process to close, then emits the done() signal with a string
        containing the compiler output as the argument.
        """
        informProc = Popen([self.compilerPath, self.sourcePath],
        cwd=self.dir, stdout=PIPE, stderr=PIPE)
        results = informProc.communicate()[0]
        self.done.emit(results.decode())
        
    def __init__(self, *args, project=Project(), **kwargs):
        """
        The "project" keyword argument is an instance of the Project class used
        to set compiler options. All other arguments are passed to the QThread
        constructor.
        """
        super().__init__(*args, **kwargs)
        self.compilerPath = project.compilerOptions['path']
        self.sourcePath = project.absMainSource()
        self.dir = project.absSourceDir()
