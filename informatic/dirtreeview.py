#!/usr/bin/env python3
# coding: utf-8

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class DirTreeView(QTreeView):
    newSelection = pyqtSignal([list])
    def __init__(self, parent=None, rootdir=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred))
        self.dirTree = QFileSystemModel()
        self.dirTree.setNameFilterDisables(False)
        self.dirTree.setNameFilters(['*.inf', '*.i6', '*.h'])
        self.dirTree.setRootPath(rootdir)
        self.setModel(self.dirTree)
        self.cd(rootdir)
        
        for column in range(1, self.dirTree.columnCount()):
            self.hideColumn(column)
    def cd(self, path):
        self.setRootIndex(self.dirTree.index(path))
    def selectionChanged(self, selected, deselected):
        self.newSelection.emit(selected.indexes())
