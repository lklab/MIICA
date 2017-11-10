from PyQt5.QtWidgets import QWidget, QMainWindow, QLayout, QGridLayout, QLineEdit, QLabel, QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

import pickle
import os
from socket import *

class ControllerManager(QMainWindow) :
	def __init__(self, projectPath) :
		super().__init__()
		self.projectPath = projectPath
		self.status = {}
		self.status["saved"] = True
		self.controller = Controller()

		# actions
		connectAction = QAction(QIcon("Resources/sample.png"), "Connect", self)
		connectAction.triggered.connect(self.connect)
		disconnectAction = QAction(QIcon("Resources/sample.png"), "Disconnect", self)
		disconnectAction.triggered.connect(self.disconnect)
		transmitApplicationAction = QAction(QIcon("Resources/sample.png"), "Transmit Application", self)
		transmitApplicationAction.triggered.connect(self.transmitApplication)
		runAction = QAction(QIcon("Resources/sample.png"), "Run", self)
		runAction.triggered.connect(self.runApplication)
		stopAction = QAction(QIcon("Resources/sample.png"), "Stop", self)
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

class Controller() :
	CMD_NONE = 0
	CMD_XMIT_APP_REQ = 1
	CMD_RUN_REQ = 2
	CMD_STOP_REQ = 3
	CMD_XMIT_APP_RES = 4
	CMD_RUN_RES = 5
	CMD_STOP_RES = 6

	VAL_SUCCESS = 1
	VAL_FAILED = 0

	def __init__(self) :
		self.connectThread = None
		self.receiverThread = None
		self.connectRequestProcessedCallback = None
		self.dataReceivedCallback = None
		self.socket = None

		self.status = {}
		self.status["connected"] = False
		self.status["connecting"] = False
		self.status["running"] = False

	# public methods
	def connect(self, address, port, connectRequestProcessedCallback, dataReceivedCallback) :
		if self.status["connected"] or self.status["connecting"] :
			return False
		self.status["connecting"] = True

		self.connectRequestProcessedCallback = connectRequestProcessedCallback
		self.dataReceivedCallback = dataReceivedCallback
		self.connectThread = ConnectThread(address, port, self.connectRequestProcessed)
		self.connectThread.start()
		return True

	def disconnect(self) :
		if not self.status["connected"] :
			return False

		if self.receiverThread :
			self.receiverThread.stop()
			self.receiverThread.wait()
			self.receiverThread = None

		if self.connectThread :
			self.connectThread.stop()
			self.connectThread.wait()
			self.connectThread = None

		self.connectRequestProcessedCallback = None
		self.dataReceivedCallback = None
		self.status["connected"] = False
		return True

	def transmitApplication(self, appPath) :
		if not self.status["connected"] or self.status["running"] :
			return False

		try :
			app = open(appPath, "rb")
			data = app.read()
			app.close()
			length = len(data)
		except :
			return False

		if not self.sendPacketHeader(self.CMD_XMIT_APP_REQ, length) :
			return False
		if not self.sendPacketData(data) :
			return False
		return True

	def runApplication(self) :
		if not self.status["connected"] or self.status["running"] :
			return False
		if not self.sendPacketHeader(self.CMD_RUN_REQ, 0) :
			return False
		self.status["running"] = True
		return True

	def stopApplication(self) :
		if not self.status["connected"] or not self.status["running"] :
			return False
		if not self.sendPacketHeader(self.CMD_STOP_REQ, 0) :
			return False
		self.status["running"] = False
		return True

	# callbacks
	def connectRequestProcessed(self, result) :
		if result :
			self.status["connected"] = True
			self.socket = self.connectThread.getSocket()
			self.receiverThread = ReceiverThread(self.socket, self.dataReceived)
			self.receiverThread.start()

		self.status["connecting"] = False
		self.connectThread.wait()

		if self.connectRequestProcessedCallback :
			self.connectRequestProcessedCallback(result)

	def dataReceived(self, data) :
		if not data :
			self.disconnect()

		(command, value) = self.getCommandFromData(data)

		if self.dataReceivedCallback :
			self.dataReceivedCallback(command, value, None)

	# private methods
	def sendPacketHeader(self, command, value) :
		bCommand = command.to_bytes(1, "big")
		bValue = value.to_bytes(4, "big")

		try :
			self.socket.send(bCommand + bValue)
			print("send %d"%command)
		except :
			self.disconnect()
			return False
		return True

	def sendPacketData(self, data) :
		try :
			self.socket.send(data)
		except :
			self.disconnect()
			return False
		return True

	def getCommandFromData(self, data) :
		command = int.from_bytes(data[:1], "big")
		value = int.from_bytes(data[1:5], "big")
		return (command, value)

class ConnectThread(QtCore.QThread) :
	signal = QtCore.pyqtSignal(bool)

	def __init__(self, address, port, callback) :
		super().__init__()
		self.address = address
		self.port = port
		self.signal.connect(callback)
		self.socket = None

	def run(self) :
		try :
			controllerAddress = (self.address, self.port)
			self.socket = socket(AF_INET, SOCK_STREAM)
			self.socket.connect(controllerAddress)
			self.signal.emit(True)
		except :
			self.signal.emit(False)

	def stop(self) :
		if self.socket :
			self.socket.close()

	def getSocket(self) :
		return self.socket

class ReceiverThread(QtCore.QThread) :
	signal = QtCore.pyqtSignal(bytes)

	def __init__(self, socket, callback) :
		super().__init__()
		self.socket = socket
		self.signal.connect(callback)
		self.flag = True

	def run(self) :
		try :
			while self.flag :
				data = self.socket.recv(1023)
				self.signal.emit(data)
				if not data :
					break
		except :
			pass
		self.stop()
		self.signal.emit(bytes(0))

	def stop(self) :
		if self.flag :
			self.flag = False
			self.socket.shutdown(SHUT_RDWR)
			self.socket.close()
