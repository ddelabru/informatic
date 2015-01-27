#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

"""
The project module contains classes for creating and managing Informatic
projects.
"""

import os.path
import json
from PyQt5.QtWidgets import *

class Project(object):
    """
    Represents an Informatic project.
    """
    def __init__(self, mainSourcePath='', sourceDir='', openSourceFiles=[],
    projectFilePath='', compilerOptions={'path': 'inform'}):
        """
        Takes five optional keyword arguments representing different
        project options: mainSourcePath, a relative filepath from the
        project file to the main source file, an empty string by
        default; sourceDir, a relative filepath from the project file to
        the main source directory, an empty string by default;
        openSourceFiles, a list of relative filepaths from the project
        file to open source Files, empty by default; projectFilePath, an
        absolute filepath to the project file, an empty string by
        default; and compilerOptions, a dictionary for the project's
        compiler options, currently containing only one key-value pair:
        "path", representing the absolute filepath to the compiler,
        "inform" by default.
        """
        self.mainSourcePath = mainSourcePath
        self.sourceDir = sourceDir
        self.openSourceFiles = openSourceFiles
        self.projectFilePath = projectFilePath
        self.compilerOptions = compilerOptions
    def absSourceDir(self):
        """
        Returns an absolute filepath to the project source directory.
        """
        fullPath = os.path.dirname(self.projectFilePath)
        fullPath = os.path.join(fullPath, self.sourceDir)
        fullPath = os.path.normpath(fullPath)
        return fullPath
    def absMainSource(self):
        """
        Returns an absolute filepath to the project's main source file.
        """
        fullPath = os.path.dirname(self.projectFilePath)
        fullPath = os.path.join(fullPath, self.mainSourcePath)
        fullPath = os.path.normpath(fullPath)
        return fullPath
    def dump(self, fp):
        """
        Takes one argument, fp, an write-opened file or file-like
        object. Prepares a dictionary containing the Informatic
        project's options and writes it to fp as a JSON object with
        indenting for human-readability.
        """
        attrDict = {}
        for attr in ['mainSourcePath', 'sourceDir', 'openSourceFiles',
        'compilerOptions']:
            attrDict[attr] = getattr(self, attr)
        json.dump(attrDict, fp, indent=2)
    def load(self, fp):
        """
        Takes one argument, fp, a read-opened file or file-like object
        containing a JSON object. Loads that JSON object as a dictionary
        containing project options and applies those options to the
        project object.
        """
        attrDict = json.load(fp)
        for attr in ['mainSourcePath', 'sourceDir', 'openSourceFiles',
        'compilerOptions']:
            setattr(self, attr, attrDict[attr])

class SourceDirPage(QWizardPage):
    """
    Page for the new project wizard that allows the user to choose the
    source directory for the project.
    """
    def __init__(self, *args, **kwargs):
        """
        Passes all arguments to the QWizardPage constructor.
        """
        super().__init__(*args, **kwargs)
        
        # The rest of this function sets up the layout of the wizard page,
        # connecting widgets to fields and functions as it does.
        self.setTitle('Source directory')
        layout = QHBoxLayout()
        label = QLabel()
        label.setText('Source directory:')
        layout.addWidget(label)
        self.lineEdit = QLineEdit()
        self.registerField('sourceDir*', self.lineEdit)
        self.lineEdit.textChanged.connect(self.completeChanged)
        layout.addWidget(self.lineEdit)
        button = QPushButton('Choose...')
        button.clicked.connect(self.chooseSourceDir)
        layout.addWidget(button)
        self.setLayout(layout)
    def chooseSourceDir(self):
        """
        Change the line edit to a directory path chosen through a File
        Dialog.
        """
        self.lineEdit.setText(QFileDialog.getExistingDirectory())
    def isComplete(self):
        """
        Allow the user to move on to the next step in creating a new
        project if the line edit contains a valid path to an existing
        directory.
        """
        if os.path.isdir(self.lineEdit.text()):
            return True
        else:
            return False

class MainSourceFilePage(QWizardPage):
    """
    Page for the new project wizard that allows the user to choose the
    main source file for the project.
    """
    def __init__(self, *args, **kwargs):
        """
        Passes all arguments to the QWizardPage constructor.
        """
        super().__init__(*args, **kwargs)
        
        # The rest of the function sets up the layout of the wizard page.
        self.setTitle('Main source file')
        layout = QVBoxLayout()
        
        # The widgets for choosing the path of a new main source file.
        self.newFileButton = QRadioButton(
        'Create new file as main source file:')
        # This radio button is connected to a function that re-evaluates which
        # widgets should be active based on user choices.
        self.newFileButton.toggled.connect(self.reEnableWidgets)
        self.registerField('newFile', self.newFileButton)
        layout.addWidget(self.newFileButton)
        newFileHBox = QHBoxLayout()
        self.newFileLineEdit = QLineEdit()
        self.newFileLineEdit.setEnabled(False)
        self.newFileLineEdit.textChanged.connect(self.completeChanged)
        self.registerField('newFilePath', self.newFileLineEdit)
        newFileHBox.addWidget(self.newFileLineEdit)
        self.newFileChooser = QPushButton('Choose...')
        self.newFileChooser.setEnabled(False)
        self.newFileChooser.clicked.connect(self.chooseNewFile)
        newFileHBox.addWidget(self.newFileChooser)
        newFileWidget = QWidget()
        newFileWidget.setLayout(newFileHBox)
        layout.addWidget(newFileWidget)
        
        # The widgets for choosing the path of an existing main source file.
        self.oldFileButton = QRadioButton(
        'Use existing file as main source file:')
        # Again, a radio button is connected to the function that re-evaluates
        # which widgets should be active.
        self.oldFileButton.toggled.connect(self.reEnableWidgets)
        self.registerField('oldFile', self.oldFileButton)
        layout.addWidget(self.oldFileButton)
        oldFileHBox = QHBoxLayout()
        self.oldFileLineEdit = QLineEdit()
        self.oldFileLineEdit.setEnabled(False)
        self.oldFileLineEdit.textChanged.connect(self.completeChanged)
        self.registerField('oldFilePath', self.oldFileLineEdit)
        oldFileHBox.addWidget(self.oldFileLineEdit)
        self.oldFileChooser = QPushButton('Choose...')
        self.oldFileChooser.setEnabled(False)
        self.oldFileChooser.clicked.connect(self.chooseOldFile)
        oldFileHBox.addWidget(self.oldFileChooser)
        oldFileWidget = QWidget()
        oldFileWidget.setLayout(oldFileHBox)
        layout.addWidget(oldFileWidget)
        self.setLayout(layout)
    def reEnableWidgets(self):
        """
        Re-evaluate which line-edit/push-button set for choosing a
        filepath is enabled, based on which radio button the user has
        selected.
        """
        if self.newFileButton.isChecked():
            self.newFileLineEdit.setEnabled(True)
            self.newFileChooser.setEnabled(True)
        else:
            self.newFileLineEdit.setEnabled(False)
            self.newFileChooser.setEnabled(False)
        if self.oldFileButton.isChecked():
            self.oldFileLineEdit.setEnabled(True)
            self.oldFileChooser.setEnabled(True)
        else:
            self.oldFileLineEdit.setEnabled(False)
            self.oldFileChooser.setEnabled(False)
        self.completeChanged.emit()
    def chooseNewFile(self):
        """
        Retrieves the filepath for an empty main source file to be
        created for the new Informatic project, and displays that
        filepath in the appropriate line-edit widget.
        """
        self.newFileLineEdit.setText(QFileDialog.getSaveFileName(
        directory=os.path.join(self.field('sourceDir'), 'main.inf'),
        filter='Inform 6 source files (*.inf)')[0])
    def chooseOldFile(self):
        """
        Retrieves the filepath for an existing main source file for the
        new Informatic project, and displays that filepath in the
        appropriate line-edit widget.
        """
        self.oldFileLineEdit.setText(QFileDialog.getOpenFileName(
        directory=self.field('sourceDir'),
        filter='Inform 6 source files (*.inf *.i6)')[0])
    def isComplete(self):
        """
        Checks whether the the wizard page is complete. Allows the user
        to continue if a radio button is checked and the corresponding
        line-edit widget is appropriately filled in.
        """
        if self.oldFileButton.isChecked():
            if os.path.isfile(self.oldFileLineEdit.text()):
                return True
            else:
                return False
        if self.newFileButton.isChecked():
            if self.newFileLineEdit.text():
                return True
            else:
                return False
        else:
            return False
    def validatePage(self):
        """
        Attempts to create the new source file before the user continues
        to the next wizard page, if the user has chosen to create a new
        source file. Stops the user if the file cannot be created.
        """
        if self.newFileButton.isChecked():
            if os.path.exists(self.newFileLineEdit.text()):
                overwriteResponse = QMessageBox.question(self,
                'File overwrite',
                'A file already exists at the filepath you have given. Is it '
                'okay to overwrite this with a blank file?')
                if overwriteResponse != QMessageBox.Yes:
                    return False
            try:
                with open(self.newFileLineEdit.text(), 'w') as newFile:
                    newFile.write('')
                return True
            except Exception as err:
                QMessageBox.critical(self, 'Filesystem error',
                'Informatic encountered an error while creating a new source '
                'file:\n\n' + str(err))
                return False
        else:
            return True

class ProjectFilePage(QWizardPage):
    """
    Page for the new project wizard that prompts the user for a name for
    the project file.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Project file')
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Project file path:'))
        self.lineEdit = QLineEdit()
        self.registerField('projectFilePath*', self.lineEdit)
        self.lineEdit.textChanged.connect(self.completeChanged)
        layout.addWidget(self.lineEdit)
        chooser = QPushButton('Choose...')
        chooser.clicked.connect(self.chooseProjectFile)
        layout.addWidget(chooser)
        self.setLayout(layout)
    def chooseProjectFile(self):
        if self.field('oldFile'):
            mainSourcePath = self.field('oldFilePath')
        if self.field('newFile'):
            mainSourcePath = self.field('newFilePath')
        defaultPath = os.path.splitext(
        os.path.basename(mainSourcePath))[0] + '.informatic'
        defaultPath = os.path.join(self.field('sourceDir'), defaultPath)
        self.lineEdit.setText(
        QFileDialog.getSaveFileName(directory=defaultPath)[0])
    def isComplete(self):
        if self.lineEdit.text():
            return True
        else:
            return False

class CompilerPage(QWizardPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Inform 6 compiler')
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Compiler path:'))
        self.lineEdit = QLineEdit()
        self.registerField('compilerPath*', self.lineEdit)
        self.lineEdit.setText('inform')
        self.lineEdit.textChanged.connect(self.completeChanged)
        layout.addWidget(self.lineEdit)
        chooser = QPushButton('Choose...')
        chooser.clicked.connect(self.chooseCompilerPath)
        layout.addWidget(chooser)
        self.setLayout(layout)
    def chooseCompilerPath(self):
        self.lineEdit.setText(QFileDialog.getOpenFileName()[0])
    def isComplete(self):
        if self.lineEdit.text():
            return True
        else:
            return False

class NewProjectWizard(QWizard):
    def __init__(self, *args, **kwargs):
        if 'project' in kwargs:
            self.project = kwargs.pop('project')
        else:
            self.project = Project()
        super().__init__(*args, **kwargs)
        self.setWindowTitle('New project')
        self.addPage(SourceDirPage())
        self.addPage(MainSourceFilePage())
        self.addPage(ProjectFilePage())
        self.addPage(CompilerPage())
    def accept(self):
        absSourceDir = self.field('sourceDir')
        projectFilePath = self.field('projectFilePath')
        projectFileDir = os.path.dirname(projectFilePath)
        self.project.sourceDir = os.path.relpath(absSourceDir,
        start=projectFileDir)
        if self.field('oldFile'):
            absMainSourcePath = self.field('oldFilePath')
            self.project.mainSourcePath = os.path.relpath(absMainSourcePath,
            start=projectFileDir)
        if self.field('newFile'):
            absMainSourcePath = self.field('newFilePath')
            self.project.mainSourcePath = os.path.relpath(absMainSourcePath,
            start=projectFileDir)
        self.project.compilerOptions = {'path': self.field('compilerPath')}
        try:
            with open(projectFilePath, 'w', encoding='utf_8') as projectFile:
                self.project.dump(projectFile)
        except Exception as err:
            QMessageBox.critical(self, 'Filesystem error',
            'Informatic encountered an error while writing a new project '
            'file:\n\n' + str(err))
        else:
            self.parent().displayProjectFile(projectFilePath)
        return super().accept()
