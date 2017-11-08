from PyQt5.QtWidgets import QWidget, QMainWindow, QLayout, QGridLayout, QLineEdit, QLabel, QAction
from PyQt5.QtGui import QIcon

import pickle
import os
from socket import *

class ControllerManager(QMainWindow) :
	def __init__(self, projectPath) :
		super().__init__()
		self.projectPath = projectPath
		self.status = {}
		self.status["connected"] = False
		self.status["running"] = False
		self.status["saved"] = True

		# actions
		connectAction = QAction(QIcon("resources/sample.png"), "Connect", self)
		connectAction.triggered.connect(self.connect)
		disconnectAction = QAction(QIcon("resources/sample.png"), "Disconnect", self)
		disconnectAction.triggered.connect(self.disconnect)
		transmitApplicationAction = QAction(QIcon("resources/sample.png"), "Transmit Application", self)
		transmitApplicationAction.triggered.connect(self.transmitApplication)
		runAction = QAction(QIcon("resources/sample.png"), "Run", self)
		runAction.triggered.connect(self.runApplication)
		stopAction = QAction(QIcon("resources/sample.png"), "Stop", self)
		stopAction.triggered.connect(self.stopApplication)

		# toolbar
		toolbar = self.addToolBar("")
		toolbar.addAction(connectAction)
		toolbar.addAction(disconnectAction)
		toolbar.addAction(transmitApplicationAction)
		toolbar.addAction(runAction)
		toolbar.addAction(stopAction)

		# widget
		self.addressEdit = QLineEdit()
		self.addressEdit.textEdited.connect(self.changed)
		self.portEdit = QLineEdit()
		self.portEdit.textEdited.connect(self.changed)

		# layout
		mainwidget = QWidget()
		mainLayout = QGridLayout()

		mainLayout.addWidget(QLabel("IP Address"), 1, 1)
		mainLayout.addWidget(QLabel("Port"), 1, 2)
		mainLayout.addWidget(self.addressEdit, 2, 1)
		mainLayout.addWidget(self.portEdit, 2, 2)

		mainLayout.setSizeConstraint(QLayout.SetFixedSize)
		mainwidget.setLayout(mainLayout)
		self.setCentralWidget(mainwidget)

		# initialze widgets from saved file
		self.initByData()

	# public methods
	def checkSaved(self) :
		return self.status["saved"]

	def save(self, projectPath) :
		data = {}
		data["ip"] = self.addressEdit.text()
		data["port"] = self.portEdit.text()

		file = open(os.path.join(self.projectPath, "ctlmgr.data"), "wb")
		pickle.dump(data, file)
		file.close()

		self.status["saved"] = True

	def setProjectPath(self, projectPath) :
		self.projectPath = projectPath

	def cleanup(self) :
		self.disconnect()
		self.stopApplication()

	# private methods
	def initByData(self) :
		try :
			file = open(os.path.join(self.projectPath, "ctlmgr.data"), "rb")
			data = pickle.load(file)
			file.close()
		except :
			data = None

		if data :
			if data.get("ip") :
				self.addressEdit.setText(data["ip"])
			if data.get("port") :
				self.portEdit.setText(data["port"])

	def changed(self, text) :
		self.status["saved"] = False

	# action handlers
	def connect(self) :
		if self.status["connected"] :
			return

		try :
			controllerAddress = (self.addressEdit.text(), int(self.portEdit.text()))
			self.controllerSocket = socket(AF_INET, SOCK_STREAM)
			self.controllerSocket.connect(controllerAddress)
			self.status["connected"] = True
		except :
			pass # TODO console

	def disconnect(self) :
		if not self.status["connected"] :
			return

		self.controllerSocket.close()
		self.status["connected"] = False

	def transmitApplication(self) :
		try :
			app = open(os.path.join(self.projectPath, "build", "PLC_APP"), "rb")
			data = app.read()
			length = len(data)
			self.controllerSocket.send(bytes(str(length), "utf-8"))
			self.controllerSocket.send(data)
			# TODO console
		except :
			pass # TODO console

	def runApplication(self) :
		if self.status["running"] and not self.status["connected"] :
			return

		try :
			self.controllerSocket.send(bytes("run", "utf-8"))
			self.status["running"] = True
		except :
			pass # TODO console

	def stopApplication(self) :
		if not self.status["running"] and not self.status["connected"] :
			return

		try :
			self.controllerSocket.send(bytes("stop", "utf-8"))
			self.status["running"] = False
		except :
			pass # TODO console
