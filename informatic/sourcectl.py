#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015-2017 Dominic Delabruere

"""
The sourcectl module contains the SourceCtl widget for editing Inform 6
source files and associated code.
"""

from PyQt5.Qsci import QsciScintilla
import os.path

from .lexer import InformLexer

# These lists may come in handy when the lexer can handle more styles.
statements = ['box', 'break', 'continue', 'do', 'font', 'for',
              'give', 'if', 'inversion', 'jump', 'move', 'new_line',
              'objectloop', 'print', 'print_ret', 'quit', 'read',
              'remove', 'restore', 'return', 'rfalse', 'rtrue', 'save',
              'spaces', 'string', 'style', 'switch', 'while']
word_operators = ['has', 'hasnt', 'in', 'notin', 'ofclass', 'or']

class SourceCtl (QsciScintilla):
    """
    A widget for editing Inform 6 source code.
    """
    def __init__(self, mainWindow=None, parent=None, filepath=None):
        """
        Takes three optional keyword arguments: mainWindow, the main
        window widget that owns the constructed widget, parent, which is
        passed QsciScintilla constructor, and filepath, which should be
        an absolute filepath to the source file to be edited.
        """
        super().__init__(parent)
        
        # If a filepath was supplied to the constructor, read the text from
        # the file into the widget.
        self.filepath = filepath
        if filepath and os.path.isfile(filepath):
            with open(self.filepath, 'r') as sourceFile:
                self.setText(sourceFile.read())
        
        # Set some formatting options for the widget
        self.setMarginWidth(0, '00000')
        lexer = InformLexer(self)
        lexer.setEditor(self)
        self.setLexer(lexer)
        
        self.mainWindow = mainWindow
        
        # The widget will keep track of whether its content has been saved.
        self.saved = True
        self.textChanged.connect(self.showUnsaved)
    def showUnsaved(self):
        """
        Called whenever the contents of the widget are changed.
        Ensures that the tab widget holding the widget indicates that
        the widget's contents have not been saved.
        """
        if self.saved:
            tabWidget = self.mainWindow.tabWidget
            tabIndex = tabWidget.indexOf(self)
            currentName = tabWidget.tabText(tabIndex)
            tabWidget.setTabText(tabIndex, '*' + currentName)
        self.saved = False
