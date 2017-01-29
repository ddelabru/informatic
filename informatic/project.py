#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2015 Dominic Delabruere

"""
The project module contains classes for creating and managing Informatic
projects.
"""

import os.path
import json
from PyQt5.QtWidgets import QWizardPage, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton, QFileDialog, QVBoxLayout, QRadioButton
from PyQt5.QtWidgets import QWidget, QMessageBox, QGroupBox, QCheckBox, QWizard

class Project(object):
    """
    Represents an Informatic project.
    """
    def __init__(self, mainSourcePath='', sourceDir='', projectFilePath='',
      compilerOptions={'path': 'inform', 'version': 'v5', 'switches': ['S']},
      terpOptions={'terpPath': 'sfrotz', 'storyFile': ''}):
        """
        Takes five optional keyword arguments representing different
        project options: mainSourcePath, a relative filepath from the
        project file to the main source file, an empty string by
        default; sourceDir, a relative filepath from the project file to
        the main source directory, an empty string by default;
        projectFilePath, an absolute filepath to the project file, an
        empty string by default; and compilerOptions, a dictionary for
        the project's compiler options, currently containing only one
        key-value pair: "path", representing the absolute filepath to
        the compiler, "inform" by default.
        """
        self.mainSourcePath = mainSourcePath
        self.sourceDir = sourceDir
        self.projectFilePath = projectFilePath
        self.compilerOptions = compilerOptions
        self.terpOptions = terpOptions
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
        for attr in ['mainSourcePath', 'sourceDir', 'compilerOptions',
          'terpOptions']:
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
        for attr in ['mainSourcePath', 'sourceDir', 'compilerOptions',
          'terpOptions']:
            setattr(self, attr, attrDict[attr])
        
        # Only load the compilerOptions and terpOptions elements if they are
        # present in the file, so Informatic can load older project files that
        # don't contain those elements
        for attr in ['compilerOptions', 'terpOptions']:
            if attr in attrDict:
                setattr(self, attr, attrDict[attr])
            else:
                setattr(self, attr, {})

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
        self.setTitle(self.tr('Source directory'))
        layout = QHBoxLayout()
        label = QLabel()
        label.setText(self.tr('Source directory:'))
        layout.addWidget(label)
        self.lineEdit = QLineEdit()
        self.registerField('sourceDir*', self.lineEdit)
        self.lineEdit.textChanged.connect(self.completeChanged)
        layout.addWidget(self.lineEdit)
        button = QPushButton(self.tr('Choose...'))
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
        self.setTitle(self.tr('Main source file'))
        layout = QVBoxLayout()
        
        # The widgets for choosing the path of a new main source file.
        self.newFileButton = QRadioButton(
        self.tr('Create new file as main source file:'))
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
        self.newFileChooser = QPushButton(self.tr('Choose...'))
        self.newFileChooser.setEnabled(False)
        self.newFileChooser.clicked.connect(self.chooseNewFile)
        newFileHBox.addWidget(self.newFileChooser)
        newFileWidget = QWidget()
        newFileWidget.setLayout(newFileHBox)
        layout.addWidget(newFileWidget)
        
        # The widgets for choosing the path of an existing main source file.
        self.oldFileButton = QRadioButton(
        self.tr('Use existing file as main source file:'))
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
        self.oldFileChooser = QPushButton(self.tr('Choose...'))
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
        filter=self.tr('Inform 6 source files (*.inf)'))[0])
    def chooseOldFile(self):
        """
        Retrieves the filepath for an existing main source file for the
        new Informatic project, and displays that filepath in the
        appropriate line-edit widget.
        """
        self.oldFileLineEdit.setText(QFileDialog.getOpenFileName(
        directory=self.field('sourceDir'),
        filter=self.tr('Inform 6 source files (*.inf *.i6)'))[0])
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
                  self.tr('File overwrite'),
                  self.tr('A file already exists at the filepath you have '
                  'given. Is it okay to overwrite this with a blank file?'))
                if overwriteResponse != QMessageBox.Yes:
                    return False
            try:
                with open(self.newFileLineEdit.text(), 'w') as newFile:
                    newFile.write('')
                return True
            except Exception as err:
                QMessageBox.critical(self, self.tr('Filesystem error'),
                self.tr('Informatic encountered an error while creating a new '
                'source file:\n\n') + str(err))
                return False
        else:
            return True

class CompilerPage(QWizardPage):
    """
    Wizard page that allows the user to set the project's compiler
    options. Used by both the new project wizard and the compiler
    options wizard.
    """
    def __init__(self, compilerOptions, *args, **kwargs):
        """
        The positional argument compilerOptions is processed as a
        dictionary containing compiler Options for an Informatic
        project. All remaining arguments are passed directly to the
        QWizardPage constructor.
        """
        self.compilerOptions = compilerOptions
        super().__init__(*args, **kwargs)
        
        # The rest of this function sets up the wizard page's layout,
        # connecting widgets to functions and wizard fields as necessary.     
        mainLayout = QVBoxLayout()
        
        pathLayout = QHBoxLayout()
        pathLayout.addWidget(QLabel(self.tr('Compiler path:')))
        self.lineEdit = QLineEdit()
        self.registerField('compilerPath*', self.lineEdit)
        self.lineEdit.setText(self.compilerOptions.get('path', 'inform'))
        self.lineEdit.textChanged.connect(self.completeChanged)
        pathLayout.addWidget(self.lineEdit)
        chooser = QPushButton(self.tr('Choose...'))
        chooser.clicked.connect(self.chooseCompilerPath)
        pathLayout.addWidget(chooser)
        mainLayout.addLayout(pathLayout)
        
        versionGroupBox = QGroupBox(self.tr('Story file version:'))
        versionLayout = QHBoxLayout()
        versionLeftLayout = QVBoxLayout()
        radio_v3 = QRadioButton(self.tr('Z-code version 3 "Standard"'))
        versionLeftLayout.addWidget(radio_v3)
        radio_v4 = QRadioButton(self.tr('Z-code version 4 "Plus"'))
        versionLeftLayout.addWidget(radio_v4)
        radio_v5 = QRadioButton(
          self.tr('Z-code version 5 "Advanced" (default)'))
        versionLeftLayout.addWidget(radio_v5)
        versionRightLayout = QVBoxLayout()
        radio_v6 = QRadioButton(self.tr('Z-code version 6 graphical'))
        versionRightLayout.addWidget(radio_v6)
        radio_v8 = QRadioButton(
          self.tr('Z-code version 8 expanded "Advanced"'))
        versionRightLayout.addWidget(radio_v8)
        radio_G = QRadioButton(self.tr('Glulx'))
        versionRightLayout.addWidget(radio_G)
        versionLayout.addLayout(versionLeftLayout)
        versionLayout.addLayout(versionRightLayout)
        versionGroupBox.setLayout(versionLayout)        
        mainLayout.addWidget(versionGroupBox)
        
        self.storyFileVersions = {
          'v3': radio_v3,
          'v4': radio_v4,
          'v5': radio_v5,
          'v6': radio_v6,
          'v8': radio_v8,
          'G': radio_G}
        
        for key in self.storyFileVersions:
            self.registerField(key, self.storyFileVersions[key])
            if self.compilerOptions.get('version', 'v5') == key:
                self.storyFileVersions[key].setChecked(True)
        
        switchesGroupBox = QGroupBox(self.tr('Popular compiler switches:'))
        switchesLayout = QHBoxLayout()
        switchesLeftLayout = QVBoxLayout()
        check_c = QCheckBox(self.tr('c: more concise error messages'))
        switchesLeftLayout.addWidget(check_c)
        check_d = QCheckBox(self.tr('d: contract double spaces after full '
          'stops in text'))
        switchesLeftLayout.addWidget(check_d)
        check_d2 = QCheckBox(self.tr('d2: contract double spaces after '
          'exclamation and question marks, too'))
        switchesLeftLayout.addWidget(check_d2)
        check_e = QCheckBox(self.tr('e: economy mode; use declared '
          'abbreviations'))
        switchesLeftLayout.addWidget(check_e)
        check_i = QCheckBox(self.tr('i: ignore default switches set in source '
          'file'))
        switchesLeftLayout.addWidget(check_i)
        check_k = QCheckBox(self.tr('k: output Infix debugging information to '
          '"gameinfo.dbg" (and switch -D on)'))
        switchesLeftLayout.addWidget(check_k)
        check_n = QCheckBox(self.tr('n: print numbers of properties, '
          'attributes and actions'))
        switchesLeftLayout.addWidget(check_n)
        check_r = QCheckBox(self.tr('r: record all the text to '
          '"gametext.txt"'))
        switchesLeftLayout.addWidget(check_r)
        switchesLayout.addLayout(switchesLeftLayout)
        switchesRightLayout = QVBoxLayout()
        check_s = QCheckBox(self.tr('s: give statistics'))
        switchesRightLayout.addWidget(check_s)
        check_u = QCheckBox(self.tr('u: work out most useful abbreviations'))
        switchesRightLayout.addWidget(check_u)
        check_w = QCheckBox(self.tr('w: disable warning messages'))
        switchesRightLayout.addWidget(check_w)
        check_B = QCheckBox(self.tr('B: use big memory model (for large V6/V7 '
          'files)'))
        switchesRightLayout.addWidget(check_B)
        check_D = QCheckBox(self.tr('D: insert "Constant DEBUG;" '
          'automatically'))
        switchesRightLayout.addWidget(check_D)
        check_H = QCheckBox(self.tr('H: use Huffman encoding to compress '
          'Glulx strings'))
        switchesRightLayout.addWidget(check_H)
        check_S = QCheckBox(self.tr('S: compile strict error-checking at '
          'run-time (on by default)'))
        switchesRightLayout.addWidget(check_S)
        check_X = QCheckBox(self.tr('X: compile with INFIX debugging '
          'facilities present'))
        switchesRightLayout.addWidget(check_X)
        switchesLayout.addLayout(switchesRightLayout)
        switchesGroupBox.setLayout(switchesLayout)
        mainLayout.addWidget(switchesGroupBox)
        
        self.switchesDict = {
          'c': check_c, 'd': check_d, 'd2': check_d2, 'd': check_d,
          'e': check_e, 'i': check_i, 'k': check_k, 'n': check_n,
          'r': check_r, 's': check_s, 'u': check_u, 'w': check_w,
          'B': check_B, 'D': check_D, 'H': check_H, 'S': check_S,
          'X': check_X}
        
        for key in self.switchesDict:
            self.registerField(key, self.switchesDict[key])
            if key in self.compilerOptions.get('switches', ['S']):
                self.switchesDict[key].setChecked(True)
        
        self.setLayout(mainLayout)
    def chooseCompilerPath(self):
        """
        Sets the contents of the page's compiler path line-edit widget
        using the output of a file dialog.
        """
        self.lineEdit.setText(QFileDialog.getOpenFileName()[0])
    def isComplete(self):
        """
        Checks whether the wizard page is complete. Allows the user to
        continue if the page's line-edit widget contains text.
        """
        if self.lineEdit.text():
            return True
        else:
            return False
    def storyFileVersion(self):
        """
        Returns a string representing the story file version switch
        that should be passed to the Inform 6 compiler, based on
        user-selected options. Default is 'v5'.
        """
        for key in self.storyFileVersions:
            if self.field(key):
                return key
        return 'v5'
    def switches(self):
        """
        Returns a list of strings representing compiler switches that
        should be passed to the Inform 6 compiler, based on
        user-selected options.
        """
        switches = []
        for key in self.switchesDict:
            if self.field(key):
                switches += [key]
        return switches

class ProjectFilePage(QWizardPage):
    """
    Page for the new project wizard that prompts the user for a name for
    the project file.
    """
    def __init__(self, *args, **kwargs):
        """
        Passes all arguments directly to the QWizardPage constructor.
        """
        super().__init__(*args, **kwargs)
        
        # The rest of this function sets up the wizard page's layout,
        # connecting widgets to functions and wizard fields as necessary.
        self.setTitle(self.tr('Project file'))
        layout = QHBoxLayout()
        layout.addWidget(QLabel(self.tr('Project file path:')))
        self.lineEdit = QLineEdit()
        self.registerField('projectFilePath*', self.lineEdit)
        self.lineEdit.textChanged.connect(self.completeChanged)
        layout.addWidget(self.lineEdit)
        chooser = QPushButton(self.tr('Choose...'))
        chooser.clicked.connect(self.chooseProjectFile)
        layout.addWidget(chooser)
        self.setLayout(layout)
    def chooseProjectFile(self):
        """
        Displays a file dialog, then fills the wizard page's line-edit
        widget with the chosen filename.
        """
        
        # The default project file name is based on the main source file name,
        # so first it is necessary to determine which field contains that
        # filename.
        if self.field('oldFile'):
            mainSourcePath = self.field('oldFilePath')
        if self.field('newFile'):
            mainSourcePath = self.field('newFilePath')
        
        # Now the default filename for the project file can be constructed.
        defaultPath = os.path.splitext(
        os.path.basename(mainSourcePath))[0] + '.informatic'
        defaultPath = os.path.join(self.field('sourceDir'), defaultPath)
        
        # Finally, launch the file dialog and use its output to fill the
        # line-edit widget.
        self.lineEdit.setText(
        QFileDialog.getSaveFileName(directory=defaultPath)[0])
    def isComplete(self):
        """
        Checks whether the wizard page is complete. Allows the user to
        continue if the page's line-edit widget contains text.
        """
        if self.lineEdit.text():
            return True
        else:
            return False

class NewProjectWizard(QWizard):
    """
    Wizard for creating a new Informatic project.
    """
    def __init__(self, *args, **kwargs):
        """
        The project keyword argument, if given, is an Informatic Project
        object that will be configured to represent the new project. All
        other arguments are passed directly to the QWizard constructor.
        """
        if 'project' in kwargs:
            self.project = kwargs.pop('project')
        else:
            self.project = Project()
        super().__init__(*args, **kwargs)
        
        # The rest of this function sets up the wizard's layout.
        self.setWindowTitle(self.tr('New project'))
        self.addPage(SourceDirPage())
        self.addPage(MainSourceFilePage())
        self.compilerPage = CompilerPage(self.project.compilerOptions)
        self.compilerPage.setTitle(self.tr('Compiler options'))
        self.addPage(self.compilerPage)
        self.addPage(ProjectFilePage())
    def accept(self):
        """
        Performs the final actions of setting up the Project object and
        writing the project file. Finishes the wizard if the project
        file is successfully written.
        """
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
        self.project.compilerOptions['version'] = \
          self.compilerPage.storyFileVersion()
        self.project.compilerOptions['switches'] = self.compilerPage.switches()
        try:
            with open(projectFilePath, 'w', encoding='utf_8') as projectFile:
                self.project.dump(projectFile)
        except Exception as err:
            QMessageBox.critical(self, self.tr('Filesystem error'),
            self.tr('Informatic encountered an error while writing a new '
            'project file:\n\n' + str(err)))
        else:
            self.parent().displayProjectFile(projectFilePath)
            return super().accept()

class CompilerOptionsWizard(QWizard):
    """
    Wizard for editing the compiler options of an Informatic project.
    """
    def __init__(self, project, *args, **kwargs):
        """
        The positional object project is interpeted as a Project object.
        All other arguments are passed directly to the QWizard
        constructor.
        """
        self.project = project
        super().__init__(*args, **kwargs)
        self.setWindowTitle(self.tr('Compiler options'))
        # In tests, the following line changed the stretch behavior of the
        # window, so it's commented out for now.
        # self.setOption(QWizard.NoBackButtonOnLastPage)
        self.compilerPage = CompilerPage(project.compilerOptions)
        self.addPage(self.compilerPage)
    def accept(self):
        """
        Processes Inform 6 compiler options and saves the project file
        when the user finishes the compiler options wizard.
        """
        
        self.project.compilerOptions['path'] = self.field('compilerPath')
        self.project.compilerOptions['version'] = \
          self.compilerPage.storyFileVersion()
        self.project.compilerOptions['switches'] = self.compilerPage.switches()
        
        try:
            with open(self.project.projectFilePath, 'w', encoding='utf_8') \
            as projectFile:
                self.project.dump(projectFile)
        except Exception as err:
            QMessageBox.critical(self, self.tr('Filesystem error'),
            self.tr('Informatic encountered an error while updating the '
            'project file:\n\n') + str(err))
        else:
            return super().accept()
