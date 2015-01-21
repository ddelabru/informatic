#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

from PyQt5.QtCore import *
from subprocess import Popen, PIPE

from .project import Project

class Compiler(QThread):
    done = pyqtSignal(str)
    
    @pyqtSlot()
    def run(self):
        informProc = Popen([self.compilerPath, self.sourcePath],
        cwd=self.dir, stdout=PIPE, stderr=PIPE)
        results = informProc.communicate()[0]
        self.done.emit(results.decode())
        
    def __init__(self, *args, project=Project(), **kwargs):
        super().__init__(*args, **kwargs)
        self.compilerPath = project.compilerOptions['path']
        self.sourcePath = project.absMainSource()
        self.dir = project.absSourceDir()
