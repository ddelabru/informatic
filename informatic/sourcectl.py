#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

"""
The sourcectl module contains the SourceCtl widget for editing Inform 6
source files and associated code.
"""

from PyQt5.QtGui import *
from PyQt5.Qsci import *
import os.path

# These lists may come in handy when the lexer can handle more styles.
statements = ['box', 'break', 'continue', 'do', 'font', 'for',
              'give', 'if', 'inversion', 'jump', 'move', 'new_line',
              'objectloop', 'print', 'print_ret', 'quit', 'read',
              'remove', 'restore', 'return', 'rfalse', 'rtrue', 'save',
              'spaces', 'string', 'style', 'switch', 'while']
word_operators = ['has', 'hasnt', 'in', 'notin', 'ofclass', 'or']

class InformLexer (QsciLexerCustom):
    """
    Provides a Qscintilla lexer for the Inform 6 language.
    """
    # The lexer  class was written using Baz Walter's QSciLexerCustom example
    # code as inspiration.
    def __init__(self, *args, **kwargs):
        """
        Passes all arguments directly to the QsciLexerCustom
        constructor.
        """
        super().__init__(*args, **kwargs)
        
        # Setup the different lexer styles, each associated with a style number
        self._styles = {
            0: 'Default',
            1: 'Comment',
            2: 'DictWord',
            3: 'String',
            4: 'Statement',
            5: 'Directive'}
        for index in self._styles:
            setattr(self, self._styles[index], index)
    
    def description(self, style):
        """
        Takes one argument, style, a style number, and returns its
        associated description, or an empty string if the style number
        is not valid.
        """
        if style in self._styles:
            return self._styles[style]
        else:
            return ''
    
    def defaultColor(self, style):
        """
        Takes one argument, style, a style number, and returns a QColor
        object representing the default color associated with that
        style.
        """
        colors = {
            self.Default: '#000000',
            self.Comment: '#FF3030',
            self.DictWord: '#FF5000',
            self.String: '#00C000',
            self.Statement: '#0000FF',
            self.Directive: '#FF00FF'}
        if style in colors:
            return QColor(colors[style])
        else:
            return super().defaultColor(style)
    def defaultFont(self, style):
        """
        Takes one argument, style, a style number, and returns a QFont
        object representing the default font associated with that style.
        """
        font = QFont()
        font.setStyleHint(QFont.Monospace, QFont.PreferDefault)
        font.setFixedPitch(True)
        font.setFamily('Courier')
        if style == self.Comment:
            font.setItalic(True)
            font.setBold(True)
        if not (style in [self.Default, self.Comment]):
            font.setBold(True)
        return font
    def styleText(self, start, end):
        """
        Takes two arguments, start and end, representing starting and
        ending positions within a QScintilla source code edit widget,
        and styles the text between these positions.
        """
        
        # I still have only a tenuous grasp on how this reimplemented function
        # is supposed to work.
        editor = self.editor()
        if editor is None:
            return
        if end > editor.length():
            end = editor.length()
        source = b''
        if end > start:
            source = editor.text().encode('utf-8')[start:end]
        if not source:
            return
        lineIndex = editor.SendScintilla(editor.SCI_LINEFROMPOSITION, start)
        currentStyle = self.Default
        if lineIndex > 0:
            lastLineEnd = editor.SendScintilla(
            editor.SCI_GETLINEENDPOSITION, lineIndex - 1)
            currentStyle = editor.SendScintilla(
            editor.SCI_GETSTYLEAT, lastLineEnd)
        if currentStyle not in [self.String, self.DictWord]:
            currentStyle = self.Default
        self.startStyling(start, 0x1f)
        for line in source.splitlines(keepends=True):
            pos = 0
            while True:
                newDQuote = line.find(b'"', pos)
                if newDQuote == -1:
                    newExMark = line.find(b'!',  pos)
                else:
                    newExMark = line.find(b'!', pos, newDQuote + 1)
                if (newExMark != -1) and (currentStyle != self.String):
                        length = newExMark - pos
                        self.setStyling(length, currentStyle)
                        pos = newExMark
                        currentStyle = self.Comment
                        break
                
                if newDQuote != -1:
                    if currentStyle == self.String:
                        length = newDQuote - pos + 2
                        self.setStyling(length, currentStyle)
                        currentStyle = self.Default
                    elif currentStyle != self.Comment:
                        length = newDQuote - pos
                        self.setStyling(length, currentStyle)
                        currentStyle = self.String
                    pos = newDQuote + 1
                else:
                    break
            length = len(line) - pos
            self.setStyling(length, currentStyle)
            if currentStyle == self.Comment:
                currentStyle = self.Default
            lineIndex += 1

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
        self.setMarginType(1, QsciScintilla.NumberMargin)
        self.setMarginLineNumbers(1, True)
        lexer = InformLexer(self)
        lexer.setEditor(self)
        self.setLexer(lexer)
        
        self.mainWindow = mainWindow
        
        # The widget will keep track of whether its content has been saved.
        self.saved = True
        self.textChanged.connect(self.showUnsaved)
    def showUnsaved(self):
        """
        Called whenever the contents of the contents of the widget are
        changed. Ensures that the tab widget holding the widget
        indicates that the widget's contents have not been saved.
        """
        if self.saved:
            tabWidget = self.mainWindow.tabWidget
            tabIndex = tabWidget.indexOf(self)
            currentName = tabWidget.tabText(tabIndex)
            tabWidget.setTabText(tabIndex, '*' + currentName)
        self.saved = False

