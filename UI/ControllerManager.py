from PyQt5.QtWidgets import (QWidget, QMainWindow, QLayout, QGridLayout, QVBoxLayout,
	QLineEdit, QLabel, QAction)

from UI.Core import Paths
from UI.Core import Icons
from UI.Core import Console

import pickle
import os
from Runtime.Controller import Controller

class ControllerManager(QMainWindow) :
	def __init__(self, projectPath) :
		super().__init__()
		self.projectPath = projectPath
		self.status = {}
		self.status["saved"] = True
		self.controller = Controller()

		# actions
		connectAction = QAction(Icons.Connect, "Connect", self)
		connectAction.triggered.connect(self.connect)
		disconnectAction = QAction(Icons.Disconnect, "Disconnect", self)
		disconnectAction.triggered.connect(self.disconnect)
		sendApplicationAction = QAction(Icons.Send, "Send Application", self)
		sendApplicationAction.triggered.connect(self.sendApplication)
		runAction = QAction(Icons.Run, "Run", self)
		runAction.triggered.connect(self.runApplication)
		stopAction = QAction(Icons.Stop, "Stop", self)
		stopAction.triggered.connect(self.stopApplication)

		# toolbar
		toolbar = self.addToolBar("")
		toolbar.addAction(connectAction)
		toolbar.addAction(disconnectAction)
		toolbar.addAction(sendApplicationAction)
		toolbar.addAction(runAction)
		toolbar.addAction(stopAction)

		# widget
		self.addressEdit = QLineEdit()
		self.addressEdit.textEdited.connect(self.changed)
		self.portEdit = QLineEdit()
		self.portEdit.textEdited.connect(self.changed)
		self.statusEdit = QLineEdit()
		self.statusEdit.setReadOnly(True)
		self.statusEdit.setText("Disconnected")

		# layout
		mainwidget = QWidget()
		mainLayout = QVBoxLayout()
		addressLayout = QGridLayout()
		statusLayout = QGridLayout()

		addressLayout.addWidget(QLabel("IP Address"), 1, 1)
		addressLayout.addWidget(QLabel("Port"), 1, 2)
		addressLayout.addWidget(self.addressEdit, 2, 1)
		addressLayout.addWidget(self.portEdit, 2, 2)

		statusLayout.addWidget(QLabel("Controller Status"), 1, 1)
		statusLayout.addWidget(self.statusEdit, 2, 1)

		mainLayout.addLayout(addressLayout)
		mainLayout.addLayout(statusLayout)
		
		statusLayout.setContentsMargins(0, 20, 0, 0)
		addressLayout.setSizeConstraint(QLayout.SetFixedSize)
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

		file = open(os.path.join(self.projectPath, Paths.ControllerData), "wb")
		pickle.dump(data, file)
		file.close()

		self.status["saved"] = True

	def setProjectPath(self, projectPath) :
		self.projectPath = projectPath

	def cleanup(self) :
		self.disconnect()

	# private methods
	def initByData(self) :
		try :
			file = open(os.path.join(self.projectPath, Paths.ControllerData), "rb")
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
		self.statusEdit.setText("Connecting...")
		self.controller.connect(self.addressEdit.text(), int(self.portEdit.text()),
			self.connectRequestProcessed, self.dataReceived)

	def disconnect(self) :
		self.controller.stopApplication()
		self.controller.disconnect()
		self.statusEdit.setText("Disconnected")

	def sendApplication(self) :
		Console.print("Transferring application...\n")
		if not self.controller.sendApplication(os.path.join(self.projectPath, "build", "PLC_APP")) :
			Console.print("Transfer failed.\n")

	def runApplication(self) :
		Console.print("Start the application...\n")
		if not self.controller.runApplication() :
			Console.print("Application start failed.\n")

	def stopApplication(self) :
		Console.print("Stop the application...\n")
		if not self.controller.stopApplication() :
			Console.print("Application stop failed.\n")

	# callbacks
	def connectRequestProcessed(self, result) :
		if result :
			self.statusEdit.setText("Connected")
		else :
			self.statusEdit.setText("Connection Failed")

	def dataReceived(self, command, value, data) :
		if not command :
			self.statusEdit.setText("Disconnected")
			return

		if command == Controller.CMD_XMIT_APP_RES :
			if value == Controller.VAL_SUCCESS :
				Console.print("Transfer completed successfully.\n")
			elif value == Controller.VAL_FAILED :
				Console.print("Transfer failed.\n")
		elif command == Controller.CMD_RUN_RES :
			if value == Controller.VAL_SUCCESS :
				self.statusEdit.setText("Running")
			elif value == Controller.VAL_FAILED :
				Console.print("Application execution failed.\n")
		elif command == Controller.CMD_STOP_RES :
			if value == Controller.VAL_SUCCESS :
				self.statusEdit.setText("Connected")
			elif value == Controller.VAL_FAILED :
				Console.print("Application stop has failed.\n")
		else :
			Console.print("Unknown response from controller : %d, %d\n"%(command, value))
