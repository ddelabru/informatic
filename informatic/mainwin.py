#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .dirtreeview import DirTreeView
from .sourcectl import SourceCtl
from .compiler import Compiler
from .project import Project, NewProjectWizard
from . import version

source_file_selectors = ('Inform 6 source files (*.inf);;'
    'Inform 6 libraries (*.h)')

class MainWin (QMainWindow):
    def checkUnsavedSourceFiles(self):
        filesUnsaved = False
        for index in range(0, self.tabWidget.count()):
            if not self.tabWidget.widget(index).saved:
                filesUnsaved = True
                break
        return filesUnsaved
    def chooseExistingFile(self):
        filepath = QFileDialog.getOpenFileName(filter=source_file_selectors)[0]
        if filepath:
            self.openSourceFile(filepath)
    def openSourceFile(self,  filepath):
        openFilepaths = []
        for index in range(0, self.tabWidget.count()):
            openFilepaths += [self.tabWidget.widget(index).filepath]
        if not (filepath in openFilepaths):
            sourceCtl = SourceCtl(mainWindow=self, filepath=filepath)
            self.tabWidget.addTab(sourceCtl, os.path.basename(filepath))
            openFilepaths += [filepath]
        self.tabWidget.setCurrentIndex(openFilepaths.index(filepath))
        for button in (self.saveFileButton, self.saveFileAsButton,
        self.closeButton):
            button.setEnabled(True)
    def newSourceTab(self):
        sourceCtl = SourceCtl(mainWindow=self)
        self.tabWidget.addTab(sourceCtl, 'Untitled')
        self.tabWidget.setCurrentWidget(sourceCtl)
    def openProjectFile(self):
        path = QFileDialog.getOpenFileName(
        filter='Informatic project files (*.informatic)')[0]
        if os.path.isfile(path):
            self.displayProjectFile(path)
    def saveSource(self, sourceCtl):
        if sourceCtl:
            filepath = sourceCtl.filepath
            if not filepath:
                self.tabWidget.setCurrentWidget(sourceCtl)
                filepath = self.getSaveFileName()
            if self.writeSourceFile(filepath, sourceCtl):
                sourceCtl.saved = True
                sourceCtl.filepath = filepath
                tabIndex = self.tabWidget.indexOf(sourceCtl)
                self.tabWidget.setTabText(tabIndex, os.path.basename(filepath))
    def saveCurrentSource(self):
        self.saveSource(self.tabWidget.currentWidget())
    def saveAllSources(self):
        for index in range(0, self.tabWidget.count()):
            self.saveSource(self.tabWidget.widget(index))
    def saveCurrentSourceAs(self):
        sourceCtl = self.tabWidget.currentWidget()
        filepath = self.getSaveFileName()
        if self.writeSourceFile(filepath, sourceCtl):
            sourceCtl.saved = True
            sourceCtl.filepath = filepath
            tabIndex = self.tabWidget.indexOf(sourceCtl)
            self.tabWidget.setTabText(tabIndex, os.path.basename(filepath))
            return True
        else:
            return False
    def getSaveFileName(self):
        return QFileDialog.getSaveFileName(
        filter=source_file_selectors)[0]
    def writeSourceFile(self, filepath, sourceCtl):
        if filepath:
            try:
                with open(filepath, 'w') as file:
                    file.write(sourceCtl.text())
            except:
                return False
        else:
            return False
        return True
    def closeTab(self, index):
        sourceCtl = self.tabWidget.widget(index)
        if not sourceCtl.saved:
            choice = QMessageBox.question(self, 'Unsaved source file',
            'The source file you are attempting to close has unsaved changes. '
            'Close without saving?')
            if choice != QMessageBox.Yes:
                return False
        self.tabWidget.removeTab(index)
        sourceCtl.destroy()
        if self.tabWidget.count() < 1:
            for button in (self.saveFileButton, self.saveFileAsButton,
            self.closeButton):
                button.setEnabled(False)
        return True
    def closeCurrentTab(self):
        self.closeTab(self.tabWidget.currentIndex())
    def selectSourceFiles(self, indexes):
        for index in indexes:
            filepath = self.treeView.dirTree.filePath(index)
            self.openSourceFile(filepath)
    def createNewProject(self):
        project = Project()
        NewProjectWizard(parent = self, project = project).show()
    def displayProjectFile(self, projectFilePath):
        self.currentProject = Project(projectFilePath=projectFilePath)
        projectFileDir = os.path.dirname(projectFilePath)
        try:
            with open(projectFilePath, 'r') as projectFile:
                self.currentProject.load(projectFile)
        except Exception as err:
            self.currentProject = Project()
            QMessageBox.critical(self, 'Project file error',
            'Informatic encountered an error while opening project file '
            + projectFilePath + ':\n\n' + str(err))
        else:
            self.currentProject.projectFilePath = projectFilePath
            
            # Attempt to close all source files already open...
            index = 0
            while self.tabWidget.count() > index:
                sourceCtl = self.tabWidget.widget(index)
                #...but don't do it if the source file has unsaved changes.
                if sourceCtl.saved:
                    self.tabWidget.removeTab(index)
                    sourceCtl.destroy()
                else:
                    index += 1
            
            self.treeView.cd(self.currentProject.absSourceDir())
            for relPath in (self.currentProject.openSourceFiles + 
            [self.currentProject.mainSourcePath]):
                absPath = os.path.normpath(
                os.path.join(projectFileDir, relPath))
                self.openSourceFile(absPath)
    def compileProject(self):
        self.compilerEdit.setText('')
        compiler = Compiler(self, project=self.currentProject)
        compiler.done.connect(self.showCompilerOutput)
        compiler.finished.connect(compiler.deleteLater)
        compiler.start()
    def showCompilerOutput(self, results):
        self.compilerEdit.setText(results)
    def showAbout(self):
        QMessageBox.about(self,
        'About Informatic',
        '<h3>Informatic ' + version + '</h3>'
        '<p>Copyright © 2015 Dominic Delabruere '
        '&lt;<a href="mailto:dominic.delabruere@gmail.com">'
        'dominic.delabruere@gmail.com</a>&gt;</p>'
        '<p>Informatic is an Inform 6 IDE written by Dominic Delabruere '
        'for Python 3 using PyQt5.</p>')
    def showAboutQt(self):
        QMessageBox.aboutQt(self)
    def closeEvent(self, event):
        if self.checkUnsavedSourceFiles():
            choice = QMessageBox.question(self, 'Unsaved source files', 
            'You have unsaved source files. Quit anyway?')
            if choice != QMessageBox.Yes:
                return event.ignore()
        settings = QSettings()
        settings.setValue('MainWin/size', self.size())
        settings.setValue('projectFilePath',
        self.currentProject.projectFilePath)
        return event.accept()
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('Informatic')
        
        fileMenu = self.menuBar().addMenu('&File')
        
        newFileButton = fileMenu.addAction('&New')
        newFileButton.triggered.connect(self.newSourceTab)
        newFileButton.setShortcuts(QKeySequence.New)
        
        openButton = fileMenu.addAction('&Open...')
        openButton.triggered.connect(self.chooseExistingFile)
        openButton.setShortcuts(QKeySequence.Open)
        
        self.saveFileButton = fileMenu.addAction('&Save')
        self.saveFileButton.setShortcuts(QKeySequence.Save)
        self.saveFileButton.triggered.connect(self.saveCurrentSource)
        
        self.saveFileAsButton = fileMenu.addAction('&Save as...')
        self.saveFileAsButton.triggered.connect(self.saveCurrentSourceAs)
        self.saveFileAsButton.setShortcuts(QKeySequence.SaveAs)
        
        self.saveAllFilesButton = fileMenu.addAction('Save a&ll')
        self.saveAllFilesButton.triggered.connect(self.saveAllSources)
        
        self.closeButton = fileMenu.addAction('&Close')
        self.closeButton.setShortcuts(QKeySequence.Close)
        self.closeButton.triggered.connect(self.closeCurrentTab)
        
        quitButton = fileMenu.addAction('&Quit')
        quitButton.setShortcuts(QKeySequence.Quit)
        quitButton.triggered.connect(self.close)
        
        # Eventually, the Edit menu will go here.
        
        # editMenu = self.menuBar().addMenu('&Edit')
        
        # prefsButton = editMenu.addAction('&Preferences...')
        # prefsButton.setShortcuts(QKeySequence.Preferences)
        
        projectMenu = self.menuBar().addMenu('&Project')
        
        newProjectButton = projectMenu.addAction('&New...')
        newProjectButton.triggered.connect(self.createNewProject)
        
        openProjectButton = projectMenu.addAction('&Open...')
        openProjectButton.triggered.connect(self.openProjectFile)
        
        compileButton = projectMenu.addAction('&Compile')
        compileButton.triggered.connect(self.compileProject)
        
        helpMenu = self.menuBar().addMenu('&Help')
        
        aboutButton = helpMenu.addAction('&About Informatic')
        aboutButton.triggered.connect(self.showAbout)
        
        aboutQtButton = helpMenu.addAction('About &Qt')
        aboutQtButton.triggered.connect(self.showAboutQt)
        
        self.treeView = DirTreeView(
            rootdir=os.getcwd()) # Widget for showing file hierarchies
        self.treeView.newSelection.connect(self.selectSourceFiles)

        self.tabWidget = QTabWidget()
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        
        self.newSourceTab()
        
        self.compilerEdit = QTextEdit()
        self.compilerEdit.setReadOnly(True)
        compilerFont = QFont()
        compilerFont.setStyleHint(QFont.Monospace, QFont.PreferDefault)
        compilerFont.setFixedPitch(True)
        compilerFont.setFamily('Courier')
        self.compilerEdit.setCurrentFont(compilerFont)
        
        self.hSplitter = QSplitter(Qt.Horizontal)
        self.hSplitter.addWidget(self.treeView)
        self.hSplitter.addWidget(self.tabWidget)
        self.hSplitter.setStretchFactor(0, 0)
        self.hSplitter.setStretchFactor(1, 1)
        
        self.vSplitter = QSplitter(Qt.Vertical)
        self.vSplitter.addWidget(self.hSplitter)
        self.vSplitter.addWidget(self.compilerEdit)
        self.vSplitter.setStretchFactor(0, 1)
        self.vSplitter.setStretchFactor(1, 0)
        self.setCentralWidget(self.vSplitter)
        
        settings = QSettings()
        size = settings.value('MainWin/size', QSize(800, 600))
        self.resize(size)
        projectFilePath = settings.value('projectFilePath', None)
        if projectFilePath:
            self.displayProjectFile(projectFilePath)
        else:
            self.currentProject = Project(projectFilePath=projectFilePath)

def main():
    app = QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    app.setOrganizationName = ('Dominic Delabruere')
    app.setApplicationName = ('Informatic')
    main = MainWin()
    main.show()
    app.exec_()
