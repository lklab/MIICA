#!/usr/bin/python3

from PyQt5.QtWidgets import (QWidget, QMainWindow, QMessageBox, QAction, 
	QFileDialog, QApplication, QSplitter, QTabWidget)
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

import sys, os
import shutil, pickle

from UI.Core import Paths
from UI.Core import Icons
from UI.Core import Platform
from UI.Core import Console

from UI.ProjectExplorer import *
from UI.ConfigurationEditor import *
from UI.ControllerManager import *

import Uppaal.UppaalProjectParser as UppaalProjectParser
import BuildSystem.CodeGenerator as CodeGenerator

class UTOPIIA(QMainWindow) :
	def __init__(self) :
		super().__init__()

		self.context = {}
		self.project = {}
		self.status = {}

		Icons.init()

		self.initUI()
		self.getContext()
		self.initProject()
		self.initStatus()

	def initUI(self) :
		# setting up actions
		newProjectAction = QAction(Icons.NewProject, "New Project", self)
		newProjectAction.setShortcut("Ctrl+N")
		newProjectAction.triggered.connect(self.newProject)
		openProjectAction = QAction(Icons.OpenProject, "Open Project...", self)
		openProjectAction.setShortcut("Ctrl+O")
		openProjectAction.triggered.connect(self.openProject)
		saveProjectAction = QAction(Icons.SaveProject, "Save Project", self)
		saveProjectAction.setShortcut("Ctrl+S")
		saveProjectAction.triggered.connect(self.saveProject)
		saveProjectAsAction = QAction(Icons.SaveProjectAs, "Save Project As...", self)
		saveProjectAsAction.setShortcut("Ctrl+Shift+S")
		saveProjectAsAction.triggered.connect(self.saveProjectAs)

		importModelAction = QAction(Icons.ImportModel, "Import Model", self)
		importModelAction.triggered.connect(self.importModel)
		editModelAction = QAction(Icons.EditModel, "Edit Model", self)
		editModelAction.triggered.connect(self.editModel)

		systemConfigurationAction = QAction(Icons.SystemConfiguration, "System Configuration", self)
		systemConfigurationAction.triggered.connect(self.systemConfiguration)
		controllerConfigurationAction = QAction(Icons.ControllerConfiguration, "Controller Manager", self)
		controllerConfigurationAction.triggered.connect(self.controllerConfiguration)

		generateAction = QAction(Icons.Generate, "Generate Application", self)
		generateAction.triggered.connect(self.generateApplication)
		regenerateAction = QAction(Icons.Regenerate, "Regenerate Application", self)
		regenerateAction.triggered.connect(self.regenerateApplication)

		# menu
		menubar = self.menuBar()
		fileMenu = menubar.addMenu("&File")
		fileMenu.addAction(newProjectAction)
		fileMenu.addAction(openProjectAction)
		fileMenu.addAction(saveProjectAction)
		fileMenu.addAction(saveProjectAsAction)

		projectMenu = menubar.addMenu("&Project")
		projectMenu.addAction(importModelAction)
		projectMenu.addAction(editModelAction)
		projectMenu.addSeparator()
		projectMenu.addAction(systemConfigurationAction)
		projectMenu.addAction(controllerConfigurationAction)
		projectMenu.addSeparator()
		projectMenu.addAction(generateAction)
		projectMenu.addAction(regenerateAction)

		# toolbar
		fileToolbar = self.addToolBar("")
		fileToolbar.addAction(newProjectAction)
		fileToolbar.addAction(openProjectAction)
		fileToolbar.addAction(saveProjectAction)
		fileToolbar.addAction(saveProjectAsAction)

		modelToolbar = self.addToolBar("")
		modelToolbar.addAction(importModelAction)
		modelToolbar.addAction(editModelAction)

		configurationToolbar = self.addToolBar("")
		configurationToolbar.addAction(systemConfigurationAction)
		configurationToolbar.addAction(controllerConfigurationAction)

		generationToolbar = self.addToolBar("")
		generationToolbar.addAction(generateAction)
		generationToolbar.addAction(regenerateAction)

		# editor area
		self.editorArea = QTabWidget()
		self.editorArea.setTabsClosable(True)
		self.editorArea.setMovable(True)
		self.editorArea.tabCloseRequested.connect(self.closeEditor)

		# editors
		self.projectExplorer = ProjectExplorer()
		self.console = Console.getDefaultConsole()

		# layout
		verticalSplitter = QSplitter(QtCore.Qt.Vertical)
		horizontalSplitter = QSplitter()

		verticalSplitter.addWidget(self.editorArea)
		verticalSplitter.addWidget(self.console)

		horizontalSplitter.addWidget(self.projectExplorer)
		horizontalSplitter.addWidget(verticalSplitter)

		verticalSplitter.setStretchFactor(0, 1)
		horizontalSplitter.setStretchFactor(1, 1)

		self.setCentralWidget(horizontalSplitter)

		# setting up window
		self.setWindowTitle("UTOPIIA - Untitled Project")
		self.setGeometry(0, 0, 960, 540)
		self.showMaximized()

	# private methods
	def getContext(self) :
		try :
			file = open(Paths.Context, "rb")
			self.context = pickle.load(file)
			file.close()
		except :
			self.context["uppaal"] = None

	def initProject(self) :
		self.setWindowTitle("UTOPIIA - Untitled Project")
		self.project["path"] = Paths.TempProjectRoot
		self.project["permanent"] = False
		self.project["name"] = "Untitled"
		self.project["model"] = None
		self.project["config"] = None
		self.project["build"] = None
		self.project["saved"] = True
		self.projectExplorer.setProject(self.project["name"])
		self.closeAllTabs()

	def initStatus(self) :
		self.status["running uppaal"] = False
		self.status["generating"] = False
		self.configurationEditor = None
		self.controllerManager = None

	def saveContext(self) :
		file = open(Paths.Context, "wb")
		pickle.dump(self.context, file)
		file.close()

	def checkSaved(self) :
		if self.project["saved"] and \
			(not self.configurationEditor or self.configurationEditor.checkSaved()) and \
			(not self.controllerManager or self.controllerManager.checkSaved()) :
			return True
		else :
			return False

	def saveProjectFile(self) :
		self.project["saved"] = True
		file = open(os.path.join(self.project["path"], Paths.Project), "wb")
		pickle.dump(self.project, file)
		file.close()

		if self.configurationEditor :
			self.configurationEditor.save(self.project["path"])

		if self.controllerManager :
			self.controllerManager.save(self.project["path"])

	def loadProjectFile(self, path) :
		try :
			file = open(os.path.join(path, Paths.Project), "rb")
			_project = pickle.load(file)
			file.close()

			_project["path"] = path
			if _project["model"] :
				_project["model"] = os.path.join(path, Paths.Model)
			if _project["config"] :
				_project["config"] = os.path.join(path, Paths.SystemConfiguration)
			if _project["build"] :
				_project["build"] = os.path.join(path, "build")
			self.setWindowTitle("UTOPIIA - " + _project["name"])
		except :
			self.errorMessage("%s\n\nInvalid Project File."%path)
			return False

		self.project = _project
		self.resetProjectExplorer()
		self.closeAllTabs()
		return True

	def importModelToProject(self, path) :
		self.project["model"] = os.path.join(self.project["path"], Paths.Model)
		shutil.copy(path, self.project["model"])
		self.projectExplorer.setModelItem("Model", self.editModel)

		if self.configurationEditor :
			self.configurationEditor.setProjectPath(self.project["model"], self.project["config"])

		self.project["saved"] = False

	def checkModelfile(self, path) :
		try :
			file = open(path, "rt")
			data = ""
			for _i in range(0, 2) :
				data += file.readline()
			file.close()
			if data == Platform.CorrectModel41 :
				return True
			elif data[:len(Platform.CorrectModel40)] == Platform.CorrectModel40 :
				return True
			else :
				return False
		except :
			return False

	def resetProjectExplorer(self) :
		self.projectExplorer.setProject(self.project["name"])
		if self.project["model"] :
			self.projectExplorer.setModelItem("Model", self.editModel)
		if self.project["config"] :
			self.projectExplorer.setSystemConfigurationItem("System Configuration", self.systemConfiguration)

	def closeAllTabs(self) :
		for count in range(self.editorArea.count()) :
			self.editorArea.removeTab(0)
		self.configurationEditor = None
		self.controllerManager = None

	# message box
	def notSavedMessage(self, ignoreButton) :
		reply = QMessageBox.question(self, "Save Project", "Do you want to save your changes?", \
			QMessageBox.Save | QMessageBox.Cancel | ignoreButton, QMessageBox.Save)
		if reply == QMessageBox.Save :
			return self.saveProject()
		elif reply == ignoreButton :
			return True
		else :
			return False

	def overwriteModelMessage(self) :
		reply = QMessageBox.question(self, "Overwrite Model", "Do you want to overwrite the existing imported model?", \
			QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
		if reply == QMessageBox.Ok :
			return True
		else :
			return False

	def newModelMessage(self) :
		reply = QMessageBox.question(self, "Imported Model is not exist", \
			"There are no imported models in the current project.\nCreate a new model?", \
			QMessageBox.Ok | QMessageBox.No, QMessageBox.Ok)
		if reply == QMessageBox.Ok :
			return True
		else :
			return False

	def informationMessage(self, message) :
		QMessageBox.information(self, "Information", message)

	def errorMessage(self, message) :
		QMessageBox.critical(self, "Error", message)

	# event callbacks
	def closeEvent(self, event) :
		if self.status["running uppaal"] :
			self.informationMessage("Quit UPPAAL first.")
			event.ignore()
			return

		if not self.checkSaved() :
			if self.notSavedMessage(QMessageBox.Discard) :
				self.closeEditor(-1)
				event.accept()
				return
			else :
				event.ignore()
				return
		else :
			self.closeEditor(-1)
			event.accept()
			return

	# signal handlers
	def uppaalTerminated(self, exitValue) :
		self.status["running uppaal"] = False
		self.uppaalWorker.wait()

	def generationTerminated(self, exitValue) :
		Console.print("Build Finished.\n")
		self.status["generating"] = False
		self.generateWorker.wait()

	# button callbacks
	def newProject(self) :
		if self.status["running uppaal"] :
			self.informationMessage("Quit UPPAAL first.")
			return False

		if not self.checkSaved() :
			if not self.notSavedMessage(QMessageBox.No) :
				return False
		self.initProject()
		return True

	def openProject(self) :
		if self.status["running uppaal"] :
			self.informationMessage("Quit UPPAAL first.")
			return False

		if not self.checkSaved() :
			if not self.notSavedMessage(QMessageBox.No) :
				return False

		path = QFileDialog.getExistingDirectory(self, "Open UTOPIIA Project", "./")
		if not path :
			return False

		if not self.loadProjectFile(path) :
			return False

		return True

	def saveProject(self) :
		if not self.project["permanent"] :
			return self.saveProjectAs()
		self.saveProjectFile()
		return True

	def saveProjectAs(self) :
		if self.status["running uppaal"] :
			self.informationMessage("Quit UPPAAL first.")
			return False

		path = QFileDialog.getExistingDirectory(self, "Save UTOPIIA Project", "./")
		if not path :
			return False

		self.project["path"] = path
		self.project["name"] = os.path.basename(path)
		self.setWindowTitle("UTOPIIA - " + self.project["name"])

		if self.project["model"] :
			tempPath = self.project["model"]
			self.project["model"] = os.path.join(self.project["path"], Paths.Model)
			shutil.copy(tempPath, self.project["model"])

		if self.project["config"] :
			self.project["config"] = os.path.join(self.project["path"], Paths.SystemConfiguration)

		if self.configurationEditor :
			self.configurationEditor.setProjectPath(self.project["model"], self.project["config"])

		if self.controllerManager :
			self.controllerManager.setProjectPath(self.project["path"])

		self.project["permanent"] = True
		self.saveProjectFile()
		self.resetProjectExplorer()
		return True

	def importModel(self) :
		if self.status["running uppaal"] :
			self.informationMessage("Quit UPPAAL first.")
			return False

		if self.project["model"] :
			if not self.overwriteModelMessage() :
				return False

		path = QFileDialog.getOpenFileName(self, "Import UPPAAL Model", "./")
		if not path[0] :
			return False
		if not self.checkModelfile(path[0]) :
			self.errorMessage("%s\n\nInvalid UPPAAL Model File."%path[0])
			return False

		self.importModelToProject(path[0])
		Console.print(path[0])
		return True

	def editModel(self) :
		if self.status["running uppaal"] :
			self.informationMessage("UPPAAL is already running.")
			return False

		if not self.context["uppaal"] or not Platform.checkUPPAALfile(self.context["uppaal"]) :
			self.context["uppaal"] = None
			self.saveContext()

			path = QFileDialog.getExistingDirectory(self, "Select UPPAAL Path", "./")
			if not path :
				return False

			self.context["uppaal"] = path
			self.saveContext()

		if not Platform.checkUPPAALfile(self.context["uppaal"]) :
			self.errorMessage("%s\n\nInvalid UPPAAL Executable."%self.context["uppaal"])
			self.context["uppaal"] = None
			self.saveContext()
			return False

		if not self.project["model"] :
			if self.newModelMessage() :
				self.importModelToProject(Paths.BasicModel)
			else :
				return False

		self.status["running uppaal"] = True
		self.uppaalWorker = UPPAALThread(self)
		self.uppaalWorker.start()
		return True

	def systemConfiguration(self) :
		if not self.configurationEditor :
			self.project["config"] = os.path.join(self.project["path"], Paths.SystemConfiguration)
			self.configurationEditor = ConfigurationEditor(self.project["model"], self.project["config"])
			self.editorArea.addTab(self.configurationEditor, "Configuration Editor")
			self.projectExplorer.setSystemConfigurationItem("System Configuration", self.systemConfiguration)
		self.editorArea.setCurrentWidget(self.configurationEditor)

	def controllerConfiguration(self) :
		if not self.controllerManager :
			self.controllerManager = ControllerManager(self.project["path"])
			self.editorArea.addTab(self.controllerManager, "Controller Manager")
		self.editorArea.setCurrentWidget(self.controllerManager)

	def generateApplication(self) :
		if self.status["generating"] :
			return

		if not self.project["model"] :
			self.errorMessage("There is no model file.")
			return
		if not self.project["config"] :
			self.errorMessage("There is no system configuration file.")
			return

		try :
			model = UppaalProjectParser.parseUppaalProject(self.project["model"])
			file = open(self.project["config"], "rb")
			sysconfig = pickle.load(file)
			file.close()
		except :
			self.errorMessage("Fail to read model and system configuration file.")
			return

		# generate model code
		modelCode = None
		headerCode = None
		(modelCode, headerCode) = CodeGenerator.generateCode(model, sysconfig)

		if not modelCode or not headerCode :
			self.errorMessage("Fail to generate code.")
			return

		# create build directory
		if not self.project["build"] :
			self.project["build"] = os.path.join(self.project["path"], "build")

		if not os.path.isdir(self.project["build"]) :
			os.mkdir(self.project["build"])

		# create model code files
		modelPath = os.path.join(self.project["build"], "model.c")
		headerPath = os.path.join(self.project["build"], "model.h")

		modelSourceFile = open(modelPath, 'w')
		modelHeaderFile = open(headerPath, 'w')
		modelSourceFile.write(modelCode)
		modelHeaderFile.write(headerCode)
		modelSourceFile.close()
		modelHeaderFile.close()

		if sysconfig["platform"] == Platform.LocalPlatform and sysconfig["os"] == Platform.LocalOS :
			localBuild = True
		else :
			localBuild = False

		platformResourcePath = Paths.getPlatformResourcePath(sysconfig["platform"], sysconfig["os"])

		if not localBuild :
			# setting up toolchain cmake file
			toolchainCmakePath = os.path.join(platformResourcePath, "toolchain.cmake")
			toolchainCmakeFile = open(toolchainCmakePath, 'r')
			toolchainCmakeData = toolchainCmakeFile.read()
			toolchainCmakeData = toolchainCmakeData%({"path" : \
				(os.path.join(platformResourcePath, "").replace("\\", "/"))})
			toolchainCmakeFile.close()

			# create toolchain cmake file
			toolchainCmakeBuildPath = os.path.join(self.project["build"], "toolchain.cmake")
			toolchainCmakeFile = open(toolchainCmakeBuildPath, 'w')
			toolchainCmakeFile.write(toolchainCmakeData)
			toolchainCmakeFile.close()

		# setting up CMakeLists.txt file
		cmakeBuild = {}
		cmakeBuild["include"] = os.path.join(Paths.BuildResource, "include").replace("\\", "/")
		cmakeBuild["libdir"] = os.path.join(platformResourcePath, "lib").replace("\\", "/")
		libListFile = open(os.path.join(platformResourcePath, "liblist.txt"), "r")
		libListData = libListFile.read()
		libListFile.close()
		cmakeBuild["lib"] = "os "
		for libPair in libListData.split("\n") :
			_data = libPair.split("=")
			if len(_data) == 2 :
				title = _data[0].strip()
				lib = _data[1].strip()
				if title == "default" or title == sysconfig["network"] :
					cmakeBuild["lib"] = cmakeBuild["lib"] + lib + " "
		cmakeBuild["lib"] = cmakeBuild["lib"].strip()

		cmakePath = os.path.join(Paths.BuildResource, "CMakeLists.txt")
		cmakeFile = open(cmakePath, "r")
		cmakeData = cmakeFile.read()
		cmakeFile.close()
		cmakeData = cmakeData%cmakeBuild

		# create CMakeLists.txt file
		cmakePath = os.path.join(self.project["build"], "CMakeLists.txt")
		cmakeFile = open(cmakePath, "w")
		cmakeFile.write(cmakeData)
		cmakeFile.close()

		# copy uppaal engine code
		resourceSourcePath = os.path.join(Paths.BuildResource, "src")
		shutil.copy(os.path.join(resourceSourcePath, "main.c"), os.path.join(self.project["build"], "main.c"))
		shutil.copy(os.path.join(resourceSourcePath, "uppaal.c"), os.path.join(self.project["build"], "uppaal.c"))

		# start auto build
		self.status["generating"] = True
		self.generateWorker = GenerateApplicationThread(self, self.project["build"], localBuild)
		self.generateWorker.start()

	def regenerateApplication(self) :
		if self.status["generating"] :
			return

		if self.project["build"] and os.path.isdir(self.project["build"]) :
			shutil.rmtree(self.project["build"])

		self.generateApplication()

	def closeEditor(self, index) :
		# close configuration editor
		if index == -1 or self.editorArea.tabText(index) == "Configuration Editor" :
			if self.configurationEditor :
				if index != -1 and not self.configurationEditor.checkSaved() :
					if not self.notSavedMessage(QMessageBox.No) :
						return
				self.configurationEditor = None

		# close controller manager
		if index == -1 or self.editorArea.tabText(index) == "Controller Manager" :
			if self.controllerManager :
				if index != -1 and not self.controllerManager.checkSaved() :
					if not self.notSavedMessage(QMessageBox.No) :
						return
				self.controllerManager.cleanup()
				self.controllerManager = None

		# close tab
		if index != -1 :
			self.editorArea.removeTab(index)

# worker threads
class UPPAALThread(QtCore.QThread) :
	signal = QtCore.pyqtSignal(int)

	def __init__(self, parent) :
		super().__init__(parent)
		self.utopiia = parent
		self.signal.connect(parent.uppaalTerminated)

	def run(self) :
		exitValue = os.system(Platform.uppaalCommand(self.utopiia.context["uppaal"], self.utopiia.project["model"]))
		self.signal.emit(exitValue)

class GenerateApplicationThread(QtCore.QThread) :
	exitSignal = QtCore.pyqtSignal(int)
	consoleSignal = QtCore.pyqtSignal(str)

	def __init__(self, parent, buildPath, isLocal=False) :
		super().__init__(parent)
		self.exitSignal.connect(parent.generationTerminated)
		self.consoleSignal.connect(Console.print)

		self.buildPath = buildPath
		self.isLocal = isLocal

	def run(self) :
		originalPath = os.getcwd()
		os.chdir(self.buildPath)

		commands = Platform.buildCommand(self.isLocal)
		for command in commands :
			file = os.popen(command)
			self.sendDataToConsole(file)

		os.chdir(originalPath)
		self.exitSignal.emit(0)

	def sendDataToConsole(self, file) :
		while True :
			data = file.readline()
			if not data :
				file.close()
				break
			self.consoleSignal.emit(data)

if __name__ == "__main__" :
	app = QApplication(sys.argv)
	utopiia = UTOPIIA()
	sys.exit(app.exec_())
