#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2017 Dominic Delabruere

"""
The interpreter module contains code for launching a game file
interpreter, to allow the user to test the game they are developing.
"""

from subprocess import Popen
from os import getcwd
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialogButtonBox, QMessageBox
from PyQt5.QtWidgets import QFileDialog

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
        terpPathButton.clicked.connect(self.chooseTerpPath)
        terpPathLayout = QHBoxLayout()
        terpPathLayout.addWidget(self.terpPathEdit)
        terpPathLayout.addWidget(terpPathButton)
        
        storyFileLabel = QLabel(self.tr('Story file:'))
        self.storyFileEdit = QLineEdit()
        self.storyFileEdit.setText(storyFile)
        storyFileButton = QPushButton(self.tr('Choose...'))
        storyFileButton.clicked.connect(self.chooseStoryFile)
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
    
    def chooseTerpPath(self):
        terpPath = QFileDialog.getOpenFileName(self,
          self.tr('Choose interpreter'), getcwd(), '')[0]
        
        if terpPath:
            self.terpPathEdit.setText(terpPath)

    def chooseStoryFile(self):
        sourceDir = self.parent().currentProject.absSourceDir()
        storyFile = QFileDialog.getOpenFileName(self,
          self.tr('Choose story file'),  sourceDir, '')[0]
        
        if storyFile:
            self.storyFileEdit.setText(storyFile)

    def accept(self):
        terpPath = self.terpPathEdit.text()
        storyFile = self.storyFileEdit.text()
        project = self.parent().currentProject
        projectFilePath = project.projectFilePath
        project.terpOptions['terpPath'] = terpPath
        project.terpOptions['storyFile'] = storyFile
        try:
            with open(projectFilePath, 'w', encoding='utf_8') as projectFile:
                project.dump(projectFile)
        except Exception as err:
            QMessageBox.critical(self.parent(),
              self.tr('Project file error'), 
              self.tr('Informatic encountered an error while saving the'
                'project file:\n\n') + str(err))
        
        try:
            Popen([terpPath, storyFile])
        except Exception as err:
            QMessageBox.critical(self.parent(),
              self.tr('Interpreter launch error'), 
              self.tr('Informatic encountered an error while launching the '
                'interpreter:\n\n') + str(err))
        super().accept()
