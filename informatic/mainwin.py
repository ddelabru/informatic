#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015-2017 Dominic Delabruere

import os
import sys
import argparse

from PyQt5.QtCore import Qt, QTranslator, QSettings, QLocale, QSize
from PyQt5.QtCore import QLibraryInfo
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QTabWidget
from PyQt5.QtWidgets import QTextEdit, QSplitter, QMessageBox, QInputDialog

from .dirtreeview import DirTreeView
from .sourcectl import SourceCtl
from .compiler import Compiler
from .project import Project, NewProjectWizard, CompilerOptionsWizard
from .interpreter import TerpDialog
from . import rc, version

# Once we import the resources module, we don't need it polluting the namespace
del rc

# These strings are used when saving and retrieving settings.
org_name = 'mrloam'
app_name = 'Informatic'

class MainWin (QMainWindow):
    def checkUnsavedSourceFiles(self):
        """
        Returns True if any open source file has unsaved content;
        otherwise, returns False.
        """
        filesUnsaved = False
        for index in range(0, self.tabWidget.count()):
            if not self.tabWidget.widget(index).saved:
                filesUnsaved = True
                break
        return filesUnsaved
    def chooseExistingFile(self):
        """
        Presents the user with a file dialog to choose an existing
        source file, then calls openSourceFile on the chosen filepath.
        """
        filepath = QFileDialog.getOpenFileName(
          filter=self.tr('Inform 6 source files (*.inf);;'
          'Inform 6 libraries (*.h)'))[0]
        if filepath:
            self.openSourceFile(filepath)
    def openSourceFile(self,  filepath):
        """
        Takes one argument, filepath, and opens the source file at
        filepath for editing if that source file is not already open.
        Brings that source file's tab to the foreground whether or not
        it was already open.
        """
        
        # Build a list of filepaths for all open source files
        openFilepaths = []
        for index in range(0, self.tabWidget.count()):
            openFilepaths += [self.tabWidget.widget(index).filepath]
        
        # If the file isn't already open, open it
        if not (filepath in openFilepaths):
            sourceCtl = SourceCtl(mainWindow=self, filepath=filepath)
            self.tabWidget.addTab(sourceCtl, os.path.basename(filepath))
            openFilepaths += [filepath]
        
        # Bring the source file's tab to the foreground
        self.tabWidget.setCurrentIndex(openFilepaths.index(filepath))
        
        # Enable file-related menu buttons, in case they were disabled by a
        # lack of open source files
        for button in (self.saveFileButton, self.saveFileAsButton,
        self.closeButton, self.undoButton, self.redoButton,
        self.gotoLineButton, self.saveAllFilesButton, self.cutButton,
        self.copyButton, self.pasteButton, self.selectAllButton):
            button.setEnabled(True)
    def newSourceTab(self):
        """
        Creates a new, empty source file tab with no associated
        filepath.
        """
        sourceCtl = SourceCtl(mainWindow=self)
        self.tabWidget.addTab(sourceCtl, self.tr('Untitled'))
        self.tabWidget.setCurrentWidget(sourceCtl)
    def openProjectFile(self):
        """
        Presents the user with a file dialog to choose an existing
        Informatic project file, then runs displayProjectFile on the
        chosen filepath.
        """
        path = QFileDialog.getOpenFileName(
        filter=self.tr('Informatic project files (*.informatic)'))[0]
        if os.path.isfile(path):
            self.displayProjectFile(path)
    def saveSource(self, sourceCtl):
        """
        Takes one argument, sourceCtl, a SourceCtl widget, and uses
        writeSourceFile to save the widget contents to either the
        associated filepath, or, if there isn't one, a filepath chosen
        through getSaveFileName.
        """
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
        """
        Calls saveSource on the active SourceCtl widget.
        """
        self.saveSource(self.tabWidget.currentWidget())
    def saveAllSources(self):
        """
        Calls saveSource on every open SourceCtl widget with unsaved
        content.
        """
        for index in range(0, self.tabWidget.count()):
            widget = self.tabWidget.widget(index)
            if not widget.saved:
                self.saveSource(self.tabWidget.widget(index))
    def saveCurrentSourceAs(self):
        """
        Calls getSaveFileName, then uses the returned filepath to save
        the contents of the active source widget with writeSourceFile.
        """
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
        """
        Opens a file dialog to select a save filename for an Inform 6
        source file, then returns the selected filename.
        """
        return QFileDialog.getSaveFileName(
          filter=self.tr('Inform 6 source files (*.inf);;'
          'Inform 6 libraries (*.h)'))[0]
    def writeSourceFile(self, filepath, sourceCtl):
        """
        Takes two arguments: filepath and sourceCtl, a SourceCtl widget.
        Attempts to write the contents of the SourceCtl widget to a file
        at filepath. Returns True if successful, returns False if
        unsuccessful or if no filepath was provided.
        """
        if filepath:
            try:
                with open(filepath, 'w') as file:
                    file.write(sourceCtl.text())
            except:
                return False
        else:
            return False
        return True
    def undo(self):
        """
        Runs the undo method of the currently active SourceCtl widget,
        if one is currently active.
        """
        if self.tabWidget.count() > 0:
            self.tabWidget.currentWidget().undo()
    def redo(self):
        """
        Runs the redo method of the currently active SourceCtl widget,
        if one is currently active.
        """
        if self.tabWidget.count() > 0:
            self.tabWidget.currentWidget().redo()
    def cut(self):
        """
        Runs the cut method of the currently active SourceCtl widget.
        """
        self.tabWidget.currentWidget().cut()
    def copy(self):
        """
        Runs the copy method of the currently active SourceCtl widget.
        """
        self.tabWidget.currentWidget().copy()
    def paste(self):
        """
        Runs the paste method of the currently active SourceCtl widget.
        """
        self.tabWidget.currentWidget().paste()
    def selectAll(self):
        """
        Uses the selectAll method of the currently active SourceCtl
        widget to select all the text it contains.
        """
        self.tabWidget.currentWidget().selectAll()
    def gotoLine(self):
        """
        Prompts the user for a line number, then makes the corresponding
        line of the active SourceCtl widget visible.
        """
        sourceCtl = self.tabWidget.currentWidget()
        lineNumber = QInputDialog.getInt(self, self.tr('Goto line'), 
         self.tr('Line number:'), value=0, min=1, max=sourceCtl.lines())[0]
          
        # Goto line will only continue if the user entered a valid line number.
        if lineNumber:
            sourceCtl.ensureLineVisible(lineNumber)
    def findFirst(self):
        """
        Prompts the user to input text via a dialog, then searches the
        text of the active SourceCtl widget for that text.
        """
        searchText, ok = QInputDialog.getText(self, self.tr('Find'),
          self.tr('Search text:'))
        if ok:
            self.tabWidget.currentWidget().findFirst(
              searchText, False, False, False, True)
    def findNext(self):
        """
        Runs the findNext method of the active SourceCtl widget.
        """
        self.tabWidget.currentWidget().findNext()
    def closeTab(self, index):
        """
        Takes one argument, index, the index of a widget displayed in
        the main window's tab widget. Attempts to close the tab
        indicated by the index and destroy the associated widget, first
        warning the user if the widget contains unsaved content. Returns
        True if the tab was successfully closed, returns False
        otherwise.
        """
        sourceCtl = self.tabWidget.widget(index)
        if not sourceCtl.saved:
            choice = QMessageBox.question(self, self.tr('Unsaved source file'),
            self.tr('The source file you are attempting to close has unsaved '
            'changes. Close without saving?'))
            if choice != QMessageBox.Yes:
                return False
        self.tabWidget.removeTab(index)
        sourceCtl.destroy()
        
        # Disable file-related buttons if there are no source tabs open.
        if self.tabWidget.count() < 1:
            for button in (self.saveFileButton, self.saveFileAsButton,
            self.closeButton, self.undoButton, self.redoButton,
            self.gotoLineButton, self.saveAllFilesButton, self.cutButton,
            self.copyButton, self.pasteButton, self.selectAllButton):
                button.setEnabled(False)
        return True
    def closeCurrentTab(self):
        """
        Calls closeTab on the currently open tab of the tab widget.
        """
        self.closeTab(self.tabWidget.currentIndex())
    def selectSourceFiles(self, indexes):
        for index in indexes:
            if not self.treeView.dirTree.isDir(index):
                filepath = self.treeView.dirTree.filePath(index)
                self.openSourceFile(filepath)
    def createNewProject(self):
        """
        Launches the new project wizard to create a new Informatic
        project.
        """
        project = Project()
        NewProjectWizard(parent = self, project = project).exec()
    def displayProjectFile(self, projectFilePath):
        """
        Takes one argument, projectFilePath, a path to an Informatic
        project file. Attempts to load a project from the file and
        display the project.
        """
        self.currentProject = Project(projectFilePath=projectFilePath)
        projectFileDir = os.path.dirname(projectFilePath)
        
        # Attempt to load the project file
        try:
            with open(projectFilePath, 'r') as projectFile:
                self.currentProject.load(projectFile)
        except Exception as err:
            # If an error occurs while loading the project file, display an
            # error dialog.
            self.currentProject = Project()
            QMessageBox.critical(self, self.tr('Project file error'),
            self.tr('Informatic encountered an error while opening project '
            'file ') + projectFilePath + ':\n\n' + str(err))
        else:
            self.currentProject.projectFilePath = projectFilePath
            
            # Attempt to close all source files already open...Hugo Labrande.
            index = 0
            while self.tabWidget.count() > index:
                sourceCtl = self.tabWidget.widget(index)
                #...but don't do it if the source file has unsaved changes.
                if sourceCtl.saved:
                    self.tabWidget.removeTab(index)
                    sourceCtl.destroy()
                else:
                    index += 1
            
            # Set the source directory viewer widget to display the project's
            # source directory
            self.treeView.cd(self.currentProject.absSourceDir())
            
            # Open the main source file
            relPath = self.currentProject.mainSourcePath
            absPath = os.path.normpath(os.path.join(projectFileDir, relPath))
            self.openSourceFile(absPath)
            
            # Enable project menu buttons
            self.compilerOptionsButton.setEnabled(True)
            self.compileButton.setEnabled(True)
            self.runButton.setEnabled(True)
    def editCompilerOptions(self):
        """
        Launches a dialog for the user to set Inform 6 compiler options.
        """
        CompilerOptionsWizard(self.currentProject, parent=self).exec()
    def compileProject(self):
        """
        Calls saveAllSources, then spawns a new thread to run the Inform
        6 compiler using the current project's compiler options.
        """
        self.saveAllSources()
        self.compilerEdit.setText('')
        compiler = Compiler(self, project=self.currentProject)
        compiler.done.connect(self.showCompilerOutput)
        compiler.finished.connect(compiler.deleteLater)
        compiler.start()
    def showCompilerOutput(self, results):
        self.compilerEdit.setText(results)
    def showTerpDialog(self):
        TerpDialog(self).show()
    def showAbout(self):
        """
        Launches the "About" dialog with information about Informatic.
        """
        QMessageBox.about(self,
        self.tr('About Informatic'),
        '<h3>Informatic ' + version + '</h3>' +
        '<p>Copyright © 2015-2017 Dominic Delabruere '
        '&lt;<a href="mailto:dominic.delabruere@gmail.com">'
        'dominic.delabruere@gmail.com</a>&gt;</p>'
        '<p>'
        + self.tr('Informatic is an Inform 6 IDE written by Dominic Delabruere'
        ' for Python 3 using PyQt5.') + '</p>'
        '<p>' + self.tr('French translation by Hugo Labrande. '
        'Spanish translation by Fernando Gegoire.') + '</p>'
        '<p>' + self.tr('Informatic can be used and distributed under the '
        'terms of the GNU General Public License, either version 3 of the '
        'License, or (at your option) any later version.') + '</p>')
    def showAboutQt(self):
        """
        Launches the "About Qt" informational dialog.
        """
        QMessageBox.aboutQt(self)
    def closeEvent(self, event):
        """
        Runs whenever the user attempts to close the main window. Warns
        the user if there are unsaved open source files. If the user
        chooses to ignore the warning or no warning is displayed, saves
        the main window's settings, then allows it to close.
        """
        if self.checkUnsavedSourceFiles():
            choice = QMessageBox.question(self,
              self.tr('Unsaved source files'), 
              self.tr('You have unsaved source files. Quit anyway?'))
            if choice != QMessageBox.Yes:
                return event.ignore()
        settings = QSettings(org_name, app_name)
        settings.setValue('MainWin/size', self.size())
        settings.setValue('projectFilePath',
        self.currentProject.projectFilePath)
        return event.accept()
    def parseArguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('project',
          help=self.tr('project file path'), nargs='?', default='')
        args = parser.parse_args()
        if args.project:
            self.displayProjectFile(args.project)
    def __init__(self, parent=None):
        """
        Passes the argument parent to the QMainWindow constructor.
        """
        super().__init__(parent)
        
        self.setWindowTitle('Informatic')
        self.setWindowIcon(QIcon(':/informatic.png'))
        
        # The code to create the Main Menu and connect its buttons to
        # appropriate functions begins here.
        fileMenu = self.menuBar().addMenu(self.tr('&File'))
        
        newFileButton = fileMenu.addAction(self.tr('&New'))
        newFileButton.triggered.connect(self.newSourceTab)
        newFileButton.setShortcut(QKeySequence.New)
        
        openButton = fileMenu.addAction(self.tr('&Open...'))
        openButton.triggered.connect(self.chooseExistingFile)
        openButton.setShortcut(QKeySequence.Open)
        
        fileMenu.addSeparator()
        
        self.saveFileButton = fileMenu.addAction(self.tr('&Save'))
        self.saveFileButton.setShortcut(QKeySequence.Save)
        self.saveFileButton.triggered.connect(self.saveCurrentSource)
        
        self.saveFileAsButton = fileMenu.addAction(self.tr('Save &as...'))
        self.saveFileAsButton.triggered.connect(self.saveCurrentSourceAs)
        self.saveFileAsButton.setShortcut(QKeySequence.SaveAs)
        
        self.saveAllFilesButton = fileMenu.addAction(self.tr('Save a&ll'))
        self.saveAllFilesButton.triggered.connect(self.saveAllSources)
        
        fileMenu.addSeparator()
        
        self.closeButton = fileMenu.addAction(self.tr('&Close'))
        self.closeButton.setShortcut(QKeySequence.Close)
        self.closeButton.triggered.connect(self.closeCurrentTab)
        
        quitButton = fileMenu.addAction(self.tr('&Quit'))
        quitButton.setShortcut(QKeySequence.Quit)
        quitButton.triggered.connect(self.close)
        
        editMenu = self.menuBar().addMenu(self.tr('&Edit'))
        
        self.undoButton = editMenu.addAction(self.tr('&Undo'))
        self.undoButton.setShortcut(QKeySequence.Undo)
        self.undoButton.triggered.connect(self.undo)
        
        self.redoButton = editMenu.addAction(self.tr('&Redo'))
        self.redoButton.setShortcut(QKeySequence.Redo)
        self.redoButton.triggered.connect(self.redo)
        
        editMenu.addSeparator()
        
        self.cutButton = editMenu.addAction(self.tr('Cu&t'))
        self.cutButton.setShortcut(QKeySequence.Cut)
        self.cutButton.triggered.connect(self.cut)
        
        self.copyButton = editMenu.addAction(self.tr('&Copy'))
        self.copyButton.setShortcut(QKeySequence.Copy)
        self.copyButton.triggered.connect(self.copy)
        
        self.pasteButton = editMenu.addAction(self.tr('&Paste'))
        self.pasteButton.setShortcut(QKeySequence.Paste)
        self.pasteButton.triggered.connect(self.paste)
        
        editMenu.addSeparator()
        
        self.selectAllButton = editMenu.addAction(self.tr('Select &all'))
        self.selectAllButton.setShortcut(QKeySequence.SelectAll)
        self.selectAllButton.triggered.connect(self.selectAll)
        
        self.findButton = editMenu.addAction(self.tr('&Find...'))
        self.findButton.setShortcut(QKeySequence.Find)
        self.findButton.triggered.connect(self.findFirst)
        
        self.findButton = editMenu.addAction(self.tr('Find &next'))
        self.findButton.setShortcut(QKeySequence.FindNext)
        self.findButton.triggered.connect(self.findNext)
        
        # If I implement a "Find previous" function, its button will go here:
        # self.findButton = editMenu.addAction(self.tr('Find pr&evious'))
        # self.findButton.setShortcuts(QKeySequence.FindPrevious)
        # self.findButton.triggered.connect(self.findPrevious)
        
        self.gotoLineButton = editMenu.addAction(self.tr('&Goto line...'))
        self.gotoLineButton.triggered.connect(self.gotoLine)
        
        # A "preferences" button will eventually go here:
        # prefsButton = editMenu.addAction(self.tr('&Preferences...'))
        # prefsButton.setShortcut(QKeySequence.Preferences)
        
        projectMenu = self.menuBar().addMenu(self.tr('&Project'))
        
        newProjectButton = projectMenu.addAction(self.tr('&New...'))
        newProjectButton.triggered.connect(self.createNewProject)
        
        openProjectButton = projectMenu.addAction(self.tr('&Open...'))
        openProjectButton.triggered.connect(self.openProjectFile)
        
        projectMenu.addSeparator()
        
        self.compilerOptionsButton = projectMenu.addAction(
          self.tr('Co&mpiler options...'))
        self.compilerOptionsButton.triggered.connect(self.editCompilerOptions)
        self.compilerOptionsButton.setEnabled(False)
        
        self.compileButton = projectMenu.addAction(self.tr('&Compile'))
        self.compileButton.triggered.connect(self.compileProject)
        self.compileButton.setShortcut(Qt.ShiftModifier + Qt.Key_F9)
        self.compileButton.setEnabled(False)
        
        self.runButton = projectMenu.addAction(self.tr('&Run...'))
        self.runButton.triggered.connect(self.showTerpDialog)
        self.runButton.setShortcut(Qt.ShiftModifier + Qt.Key_F5)
        self.runButton.setEnabled(False)
        
        helpMenu = self.menuBar().addMenu(self.tr('&Help'))
        
        aboutButton = helpMenu.addAction(self.tr('&About Informatic'))
        aboutButton.triggered.connect(self.showAbout)
        
        aboutQtButton = helpMenu.addAction(self.tr('About &Qt'))
        aboutQtButton.triggered.connect(self.showAboutQt)
        
        # Code to create the main window's primary widgets begins here.
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
        
        # Retrieve main window settings if any were saved previously
        settings = QSettings(org_name, app_name)
        size = settings.value('MainWin/size', QSize(800, 600))
        self.resize(size)
        projectFilePath = settings.value('projectFilePath', None)
        
        # Open the project file at the path saved by the last closed main
        # window instance, if any.
        if projectFilePath:
            self.displayProjectFile(projectFilePath)
        else:
            self.currentProject = Project(projectFilePath=projectFilePath)

def main():
    """
    Provides the main entry point for Informatic. Starts a new
    application and opens the main window, then waits for these to
    close.
    """
    app = QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    
    # Uncomment and edit the following line to set the locale on application
    # startup. This may be useful for testing translations.
    # QLocale.setDefault(QLocale(QLocale.Spanish))
    
    # Use translations for Informatic's phrases, if available
    informaticTranslator = QTranslator()
    if informaticTranslator.load(QLocale(), 'informatic', '_', ':', '.qm'):
      app.installTranslator(informaticTranslator)
    
    # If there is a directory in the executable path called 'qt_translations',
    # as there may be for a "frozen" Informatic executable manually bundled
    # with Qt translations files, we will look for the translations files
    # there. Otherwise, we will attempt to load them from the standard Qt
    # translations directory.
    qtTranslationsDir = os.path.dirname(sys.executable)
    qtTranslationsDir = os.path.join(qtTranslationsDir, 'qt_translations')
    if not os.path.isdir(qtTranslationsDir):
        qtTranslationsDir = QLibraryInfo.location(
          QLibraryInfo.TranslationsPath)
    
    # Use translations for Qt built-in phrases
    qtTranslator = QTranslator()
    if qtTranslator.load(QLocale(), 'qt', '_', qtTranslationsDir, '.qm'):
      app.installTranslator(qtTranslator)
    
    main = MainWin()
    main.show()
    main.parseArguments()
    sys.exit(app.exec_())
