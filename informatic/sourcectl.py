#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

'''
informatic.sourcectl

The informatic.sourcectl module contains the SourceCtl widget for editing
source files and associated code.
'''

from PyQt5.QtGui import *
from PyQt5.Qsci import *
import os.path

statements = ['box', 'break', 'continue', 'do', 'font', 'for',
              'give', 'if', 'inversion', 'jump', 'move', 'new_line', 
              'objectloop', 'print', 'print_ret', 'quit', 'read',
              'remove', 'restore', 'return', 'rfalse', 'rtrue', 'save', 
              'spaces', 'string', 'style', 'switch', 'while']
word_operators = ['has', 'hasnt', 'in', 'notin', 'ofclass', 'or']

class InformLexer (QsciLexerCustom):
    '''
    The InformLexer class provides a Qscintilla lexer for the Inform 6 language.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        if style in self._styles:
            return self._styles[style]
        else:
            return ''
    def defaultColor(self, style):
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
            lastLineEnd = editor.SendScintilla(editor.SCI_GETLINEENDPOSITION, lineIndex - 1)
            currentStyle = editor.SendScintilla(editor.SCI_GETSTYLEAT, lastLineEnd)
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
    def __init__(self, mainWindow=None, parent=None, filepath=None):
        super().__init__(parent)
        self.setMarginLineNumbers(1, True)
        lexer = InformLexer(self)
        lexer.setEditor(self)
        self.setLexer(lexer)
        self.filepath = filepath
        if filepath and os.path.isfile(filepath):
            with open(self.filepath, 'r') as sourceFile:
                self.setText(sourceFile.read())
        
        self.mainWindow = mainWindow
        self.saved = True
        self.textChanged.connect(self.showUnsaved)
    def showUnsaved(self):
        if self.saved:
            tabWidget = self.mainWindow.tabWidget
            tabIndex = tabWidget.indexOf(self)
            currentName = tabWidget.tabText(tabIndex)
            tabWidget.setTabText(tabIndex, '*' + currentName)
        self.saved = False

