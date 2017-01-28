#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2017 Dominic Delabruere

"""
The interpreter module contains code for launching a game file
interpreter, to allow the user to test the game they are developing.
"""

from subprocess import run
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialogButtonBox

class TerpDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        
        if 'terpPath' in parent.currentProject.terpOptions:
            terpPath = parent.currentProject.terpOptions['terpPath']
        else:
            terpPath = 'sfrotz'
        
        if 'storyFile' in parent.currentProject.terpOptions:
            storyFile = parent.currentProject.terpOptions['storyFile']
        else:
            storyFile = ''
        
        terpPathLabel = QLabel(self.tr('Interpreter path:'))
        self.terpPathEdit = QLineEdit()
        self.terpPathEdit.setText(terpPath)
        terpPathButton = QPushButton(self.tr('Choose...'))
        terpPathLayout = QHBoxLayout()
        terpPathLayout.addWidget(self.terpPathEdit)
        terpPathLayout.addWidget(terpPathButton)
        
        storyFileLabel = QLabel(self.tr('Story file:'))
        self.storyFileEdit = QLineEdit()
        self.storyFileEdit.setText(storyFile)
        storyFileButton = QPushButton(self.tr('Choose...'))
        storyFileLayout = QHBoxLayout()
        storyFileLayout.addWidget(self.storyFileEdit)
        storyFileLayout.addWidget(storyFileButton)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok |
          QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        layout = QVBoxLayout()
        layout.addWidget(terpPathLabel)
        layout.addLayout(terpPathLayout)
        layout.addWidget(storyFileLabel)
        layout.addLayout(storyFileLayout)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        
        self.setWindowTitle(self.tr('Run project'))
    
    def accept(self):
        terpPath = self.terpPathEdit.text()
        storyFile = self.storyFileEdit.text()
        run([terpPath, storyFile])
        super().accept()
