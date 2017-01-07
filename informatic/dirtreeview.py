#!/usr/bin/env python3
# coding: utf-8

"""
The dirtreeview module contains the DirTreeView class.
"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTreeView, QSizePolicy, QFileSystemModel

class DirTreeView(QTreeView):
    """
    A widget class used to display the contents of an Informatic project source
    directory.
    """
    newSelection = pyqtSignal([list])
    
    def __init__(self, parent=None, rootdir=None):
        """
        The rootdir keyword argument is a filepath for a directory initialized
        as the root directory whose contents are displayed by the widget.
        """
        
        # Invoke the QTreeView constructor
        super().__init__(parent)
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        # The widget's contents are based on a file system model
        self.dirTree = QFileSystemModel()
        
        # Display only files with filename extensions commonly used for Inform 6
        # source files
        self.dirTree.setNameFilterDisables(False)
        self.dirTree.setNameFilters(['*.inf', '*.i6', '*.h'])
        
        self.dirTree.setRootPath(rootdir)
        self.setModel(self.dirTree)
        self.cd(rootdir)
        
        # Hide all but the first column, which holds the filename
        for column in range(1, self.dirTree.columnCount()):
            self.hideColumn(column)
            
    def cd(self, path):
        """
        Takes one argument, path, a directory filepath, and changes the root
        directory displayed by the widget to the directory at that filepath.
        """
        self.setRootIndex(self.dirTree.index(path))
        
    def selectionChanged(self, selected, deselected):
        """
        Emits the newSelection signal with a list of selected items whenever the
        selection of items in the file tree is changed.
        """
        self.newSelection.emit(selected.indexes())
