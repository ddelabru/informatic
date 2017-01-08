# coding: utf-8
# Copyright (c) 2017 Dominic Delabruere

from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor, QFont

class InformLexer(QsciLexerCustom):
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
        font.setPointSize(10)
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
        editor = self.editor()
        if editor == None:
            return
        if end > editor.length():
            end = editor.length()
        source = b''
        if end > start:
            source = editor.text().encode('utf-8')[start:end]
        if not source:
            return
        currentStyle = self.Default
        lineIndex = editor.SendScintilla(editor.SCI_LINEFROMPOSITION, start)
        if lineIndex > 0:
            currentStyle = editor.SendScintilla(
              editor.SCI_GETSTYLEAT, start - 1)
        nextStyle = currentStyle
        self.startStyling(start, 0x1f)
        for pos in range(0, len(source)):
            currentStyle = nextStyle
            if (source[pos] == ord(b'!')) and (currentStyle != self.String):
                currentStyle = self.Comment
                nextStyle = self.Comment
            elif (source[pos] == ord(b'\n')) and (currentStyle == self.Comment):
                currentStyle = self.Default
                nextStyle = self.Default
            elif (source[pos] == ord(b'"')) and (currentStyle != self.Comment):
                if currentStyle == self.String:
                    nextStyle = self.Default
                else:
                    currentStyle = self.String
                    nextStyle = self.String
            self.setStyling(1, currentStyle)
