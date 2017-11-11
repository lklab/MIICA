from PyQt5.QtWidgets import QWidget, QMainWindow, QLayout, QGridLayout, QLineEdit, QLabel, QAction

from UI.Core import Paths
from UI.Core import Icons

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
		transmitApplicationAction = QAction(Icons.Transmit, "Transmit Application", self)
		transmitApplicationAction.triggered.connect(self.transmitApplication)
		runAction = QAction(Icons.Run, "Run", self)
		runAction.triggered.connect(self.runApplication)
		stopAction = QAction(Icons.Stop, "Stop", self)
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
		self.controller.connect(self.addressEdit.text(), int(self.portEdit.text()),
			self.connectRequestProcessed, self.dataReceived)

	def disconnect(self) :
		self.controller.stopApplication()
		self.controller.disconnect()

	def transmitApplication(self) :
		self.controller.transmitApplication(os.path.join(self.projectPath, "build", "PLC_APP"))

	def runApplication(self) :
		self.controller.runApplication()

	def stopApplication(self) :
		self.controller.stopApplication()

	# callbacks
	def connectRequestProcessed(self, result) :
		if result :
			print("connected!") # TODO : test
		else :
			print("conntection failed!") # TODO : test

	def dataReceived(self, command, value, data) :
		if command == Controller.CMD_XMIT_APP_RES :
			print("Transmit result %d"%value) # TODO : test
		elif command == Controller.CMD_RUN_RES :
			print("Run result %d"%value) # TODO : test
		elif command == Controller.CMD_STOP_RES :
			print("Stop result %d"%value) # TODO : test
		else :
			print("unknown : %d, %d"%(command, value))
