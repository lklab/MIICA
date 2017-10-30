#!/usr/bin/python3

from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QFileDialog, QApplication)
from PyQt5.QtGui import QIcon

import sys, os
import shutil, pickle

class UTOPIIA(QMainWindow) :
	context = {}

	project = {}
	saved = True

	def __init__(self) :
		super().__init__()
		self.getContext()
		self.initProject()
		self.initUI()

	def initUI(self) :
		# setting up actions
		newProject = QAction(QIcon('resources/sample.png'), 'New Project', self)
		newProject.triggered.connect(self.createNewProject)
		openProject = QAction(QIcon('resources/sample.png'), 'Open Project', self)
		openProject.triggered.connect(self.openProjectDialog)
		saveProject = QAction(QIcon('resources/sample.png'), 'Save Project', self)
		saveProject.triggered.connect(self.saveProject)

		importUPPAAL = QAction(QIcon('resources/sample.png'), 'Import UPPAAL Project', self)
		importUPPAAL.triggered.connect(self.importUPPAALDialog)
		editUPPAAL = QAction(QIcon('resources/sample.png'), 'Edit UPPAAL Project', self)
		editUPPAAL.triggered.connect(self.editUPPAAL)

		# menu
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(newProject)
		fileMenu.addAction(openProject)
		fileMenu.addAction(saveProject)

		projectMenu = menubar.addMenu('&Project')
		projectMenu.addAction(importUPPAAL)
		projectMenu.addAction(editUPPAAL)
		projectMenu.addSeparator()

		# toolbar
		fileToolbar = self.addToolBar('')
		fileToolbar.addAction(newProject)
		fileToolbar.addAction(openProject)
		fileToolbar.addAction(saveProject)

		projectToolbar = self.addToolBar('')
		projectToolbar.addAction(importUPPAAL)
		projectToolbar.addAction(editUPPAAL)

		# status bar
		self.statusBar().showMessage('Ready')

		# setting up window
		self.setWindowTitle('UTOPIIA - Untitled Project')
		self.setGeometry(0, 0, 960, 540)
#		self.showMaximized()
		self.show()

	def initProject(self) :
		self.setWindowTitle('UTOPIIA - Untitled Project')

		self.project['path'] = None
		self.project['name'] = 'Untitled'
		self.project['model'] = None
	
	def getContext(self) :
		try :
			file = open(os.path.join('resources', 'context.data'), 'rb')
			self.context = pickle.load(file)
			file.close()
		except :
			self.context['uppaal'] = None

	def saveContext(self) :
		file = open(os.path.join('resources', 'context.data'), 'wb')
		pickle.dump(self.context, file)
		file.close()

	# evant callback
	def createNewProject(self) :
		if self.saved :
			self.initProject()
			self.saved = False

	def openProjectDialog(self) :
		if self.saved :
			fname = QFileDialog.getExistingDirectory(self, 'Open UTOPIIA Project', './')
			if fname :
				file = open(os.path.join(fname, 'project.utopiia'), 'rb')
				self.project = pickle.load(file)
				file.close()
				self.setWindowTitle('UTOPIIA - ' + self.project['name'])
			else :
				pass

	def saveProject(self) :
		if not self.project.get('path') :
			fname = QFileDialog.getExistingDirectory(self, 'Save UTOPIIA Project', './')
			if not fname :
				return
			self.project['path'] = fname
			self.project['name'] = os.path.basename(fname)
			self.setWindowTitle('UTOPIIA - ' + self.project['name'])

		file = open(os.path.join(self.project['path'], 'project.utopiia'), 'wb')
		pickle.dump(self.project, file)
		file.close()
		self.saved = True

	def importUPPAALDialog(self) :
		fname = QFileDialog.getOpenFileName(self, 'Import UPPAAL Project', './')
		if fname[0] :
			self.project['model'] = os.path.join(self.project['path'], 'model.xml')
			shutil.copy(fname[0], self.project['model'])
			self.saved = False
		else :
			pass

	def editUPPAAL(self) :
		if not self.context['uppaal'] :
			fname = QFileDialog.getOpenFileName(self, 'Select UPPAAL Path', './')
			if fname[0] :
				self.context['uppaal'] = fname[0]
				self.saveContext()
			else :
				return

		if not self.project['model'] :
			self.project['model'] = os.path.join(project['path'], 'model.xml')
			shutil.copy(os.path.join('resource', 'model.xml'), self.project['model'])

		os.system(self.context['uppaal'] + " " + self.project['model'] + " &")

if __name__ == '__main__' :
	app = QApplication(sys.argv)
	ex = UTOPIIA()
	sys.exit(app.exec_())
