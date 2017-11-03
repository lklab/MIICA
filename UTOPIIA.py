#!/usr/bin/python3

from PyQt5.QtWidgets import (QWidget, QMainWindow, QMessageBox, QAction, 
	QFileDialog, QApplication, QSplitter, QTextEdit, QPushButton)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize
from PyQt5 import QtCore

import sys, os
import shutil, pickle

from ProjectExplorer import *

CORRECT_UPPAAL_4_1 = """#!/usr/bin/env bash

#  
# Run this script to start UPPAAL 4.1.x.
#
"""
CORRECT_UPPAAL_4_0 = """#!/usr/bin/env bash

#  
# Run this script to start UPPAAL 4.0.x.
#
"""
CORRECT_MODEL_4_1 = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' \
'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
"""
CORRECT_MODEL_4_0 = \
"""<?xml version='1.0' encoding='utf-8'?><!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' \
'http://www.it.uu.se/research/group/darts/uppaal/flat-1_1.dtd'><nta><declaration>"""

class UTOPIIA(QMainWindow) :
	context = {}
	project = {}
	status = {}

	def __init__(self) :
		super().__init__()
		self.initUI()
		self.getContext()
		self.initProject()
		self.initStatus()

	def initUI(self) :
		# setting up actions
		newProjectAction = QAction(QIcon("resources/sample.png"), "New Project", self)
		newProjectAction.setShortcut("Ctrl+N")
		newProjectAction.triggered.connect(self.newProject)
		openProjectAction = QAction(QIcon("resources/sample.png"), "Open Project...", self)
		openProjectAction.setShortcut("Ctrl+O")
		openProjectAction.triggered.connect(self.openProject)
		saveProjectAction = QAction(QIcon("resources/sample.png"), "Save Project", self)
		saveProjectAction.setShortcut("Ctrl+S")
		saveProjectAction.triggered.connect(self.saveProject)
		saveProjectAsAction = QAction(QIcon("resources/sample.png"), "Save Project As...", self)
		saveProjectAsAction.setShortcut("Ctrl+Shift+S")
		saveProjectAsAction.triggered.connect(self.saveProjectAs)

		importModelAction = QAction(QIcon("resources/sample.png"), "Import Model", self)
		importModelAction.triggered.connect(self.importModel)
		editModelAction = QAction(QIcon("resources/sample.png"), "Edit Model", self)
		editModelAction.triggered.connect(self.editModel)

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

		# toolbar
		fileToolbar = self.addToolBar("")
		fileToolbar.addAction(newProjectAction)
		fileToolbar.addAction(openProjectAction)
		fileToolbar.addAction(saveProjectAction)
		fileToolbar.addAction(saveProjectAsAction)

		projectToolbar = self.addToolBar("")
		projectToolbar.addAction(importModelAction)
		projectToolbar.addAction(editModelAction)

		# editors
		_icon = QIcon("resources/sample.png")
		self.projectExplorer = ProjectExplorer()
		editor = QPushButton()
		editor.setIcon(_icon)
		editor.setIconSize(QSize(500, 500))
		console = QTextEdit()
		rightView = QWidget()

		# layout
		verticalSplitter = QSplitter(QtCore.Qt.Vertical, rightView)
		horizontalSplitter = QSplitter(self)

		verticalSplitter.addWidget(editor)
		verticalSplitter.addWidget(console)

		horizontalSplitter.addWidget(self.projectExplorer)
		horizontalSplitter.addWidget(verticalSplitter)

		verticalSplitter.setStretchFactor(0, 1)
		horizontalSplitter.setStretchFactor(1, 1)

		self.setCentralWidget(horizontalSplitter)

		# setting up window
		self.setWindowTitle("UTOPIIA - Untitled Project")
		self.setGeometry(0, 0, 960, 540)
		self.showMaximized()
#		self.show()

	# private methods
	def getContext(self) :
		try :
			file = open(os.path.join("resources", "context.data"), "rb")
			self.context = pickle.load(file)
			file.close()
		except :
			self.context["uppaal"] = None

	def initProject(self) :
		self.setWindowTitle("UTOPIIA - Untitled Project")
		self.project["path"] = None
		self.project["name"] = "Untitled"
		self.project["model"] = None
		self.project["saved"] = True
		self.projectExplorer.setProject(self.project["name"])

	def initStatus(self) :
		self.status["running uppaal"] = False

	def saveContext(self) :
		file = open(os.path.join("resources", "context.data"), "wb")
		pickle.dump(self.context, file)
		file.close()

	def saveProjectFile(self) :
		if self.project["path"] :
			self.project["saved"] = True
			file = open(os.path.join(self.project["path"], "project.utopiia"), "wb")
			pickle.dump(self.project, file)
			file.close()

	def loadProjectFile(self, path) :
		try :
			file = open(os.path.join(path, "project.utopiia"), "rb")
			_project = pickle.load(file)
			file.close()

			_project["path"] = path
			if _project["model"] :
				_project["model"] = os.path.join(path, "model.xml")
			self.setWindowTitle("UTOPIIA - " + _project["name"])
		except :
			self.errorMessage("%s\n\nInvalid Project File."%path)
			return False

		self.project = _project
		self.projectExplorer.setProject(self.project["name"])
		if self.project["model"] :
			self.projectExplorer.setModelItem(self.editModel)
		return True

	def importModelToProject(self, path) :
		if not self.project["path"] :
			self.project["model"] = os.path.join("resources", "model.xml.temp")
		else :
			self.project["model"] = os.path.join(self.project["path"], "model.xml")
		shutil.copy(path, self.project["model"])
		self.projectExplorer.setModelItem(self.editModel)
		self.project["saved"] = False

	def checkUPPAALfile(self, path) :
		try :
			file = open(path, "rt")
			data = ""
			for _i in range(0, 5) :
				data += file.readline()
			file.close()
			if data == CORRECT_UPPAAL_4_1 :
				return True
			elif data == CORRECT_UPPAAL_4_0 :
				return True
			else :
				return False
		except :
			return False

	def checkModelfile(self, path) :
		try :
			file = open(path, "rt")
			data = ""
			for _i in range(0, 2) :
				data += file.readline()
			file.close()
			if data == CORRECT_MODEL_4_1 :
				return True
			elif data[:len(CORRECT_MODEL_4_0)] == CORRECT_MODEL_4_0 :
				return True
			else :
				return False
		except :
			return False

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

		if not self.project["saved"] :
			if self.notSavedMessage(QMessageBox.Discard) :
				event.accept()
				return
			else :
				event.ignore()
				return
		else :
			event.accept()
			return

	# signal handlers
	def uppaalTerminated(self, exitValue) :
		self.status["running uppaal"] = False

	# button callbacks
	def newProject(self) :
		if self.status["running uppaal"] :
			self.informationMessage("Quit UPPAAL first.")
			return False

		if not self.project["saved"] :
			if not self.notSavedMessage(QMessageBox.No) :
				return False
		self.initProject()
		return True

	def openProject(self) :
		if self.status["running uppaal"] :
			self.informationMessage("Quit UPPAAL first.")
			return False

		if not self.project["saved"] :
			if not self.notSavedMessage(QMessageBox.No) :
				return False

		path = QFileDialog.getExistingDirectory(self, "Open UTOPIIA Project", "./")
		if not path :
			return False

		if not self.loadProjectFile(path) :
			return False

		return True

	def saveProject(self) :
		if not self.project["path"] :
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
			self.project["model"] = os.path.join(self.project["path"], "model.xml")
			shutil.copy(tempPath, self.project["model"])

		self.saveProjectFile()
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
		return True

	def editModel(self) :
		if self.status["running uppaal"] :
			self.informationMessage("UPPAAL is already running.")
			return False

		if not self.context["uppaal"] or not self.checkUPPAALfile(self.context["uppaal"]) :
			self.context["uppaal"] = None
			self.saveContext()

			path = QFileDialog.getOpenFileName(self, "Select UPPAAL Path", "./")
			if not path[0] :
				return False

			self.context["uppaal"] = path[0]
			self.saveContext()

		if not self.checkUPPAALfile(self.context["uppaal"]) :
			self.errorMessage("%s\n\nInvalid UPPAAL Executable."%self.context["uppaal"])
			self.context["uppaal"] = None
			self.saveContext()
			return False

		if not self.project["model"] :
			if self.newModelMessage() :
				self.importModelToProject(os.path.join("resources", "model.xml"))
			else :
				return False

		self.status["running uppaal"] = True
		uppaalWorker = UPPAALThread(self)
		uppaalWorker.start()
		return True

# worker threads
class UPPAALThread(QtCore.QThread) :
	utopiia = None
	signal = QtCore.pyqtSignal(int)

	def __init__(self, parent) :
		super().__init__(parent)
		self.utopiia = parent
		self.signal.connect(parent.uppaalTerminated)

	def run(self) :
		exitValue = os.system(self.utopiia.context["uppaal"] + " " + self.utopiia.project["model"])
		self.signal.emit(exitValue)

if __name__ == "__main__" :
	app = QApplication(sys.argv)
	utopiia = UTOPIIA()
	sys.exit(app.exec_())
