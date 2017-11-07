from PyQt5.QtWidgets import (QWidget, QMainWindow, QLayout, QVBoxLayout,
	QHBoxLayout, QGridLayout, QListWidget, QListWidgetItem, QLabel,
	QLineEdit, QComboBox, QAction, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

import os, pickle
import UppaalProjectParser
import ResourceManager

class ConfigurationItem(QWidget) :
	def __init__(self) :
		super().__init__()
		self.changedCallback = None

	def setChangedCallback(self, callback) :
		self.changedCallback = callback

	def changed(self, dummy) :
		if self.changedCallback :
			self.changedCallback()

class TaskConfigurationItem(ConfigurationItem) :
	def __init__(self, dataList) :
		super().__init__()
		self.dataList = dataList

		# widget
		self.taskSelect = QComboBox()
		if self.dataList :
			for data in self.dataList :
				self.taskSelect.addItem(data)
		self.taskSelect.setCurrentIndex(-1)
		self.taskSelect.currentIndexChanged.connect(self.changed)

		# layout
		mainLayout = QVBoxLayout(self)
		mainLayout.addWidget(QLabel("Task type"))
		mainLayout.addWidget(self.taskSelect)

	def setData(self, value) :
		self.taskSelect.setCurrentIndex(self.taskSelect.findText(value["type"]))

	def getData(self) :
		data = {}
		data["type"] = self.taskSelect.currentText()
		return data

	def refresh(self, dataList) :
		self.dataList = dataList
		value = self.getData()

		for count in range(self.taskSelect.count()) :
			self.taskSelect.removeItem(0)
		for data in self.dataList :
			self.taskSelect.addItem(data)

		self.setData(value)

class IOConfigurationItem(ConfigurationItem) :
	def __init__(self, dataList) :
		super().__init__()
		self.dataList = dataList

		# widget
		self.variableSelect = QComboBox()
		if self.dataList :
			for data in self.dataList :
				self.variableSelect.addItem(data)
		self.variableSelect.setCurrentIndex(-1)
		self.variableSelect.currentIndexChanged.connect(self.changed)

		self.addressEdit = QLineEdit()
		self.addressEdit.textEdited.connect(self.changed)

		self.directionSelect = QComboBox()
		self.directionSelect.addItem("In")
		self.directionSelect.addItem("Out")
		self.directionSelect.setCurrentIndex(-1)
		self.directionSelect.currentIndexChanged.connect(self.changed)

		# layout
		mainLayout = QGridLayout(self)
		mainLayout.addWidget(QLabel("Model Variable"), 1, 1)
		mainLayout.addWidget(QLabel("I/O Address"), 1, 2)
		mainLayout.addWidget(QLabel("Direction"), 1, 3)
		mainLayout.addWidget(self.variableSelect, 2, 1)
		mainLayout.addWidget(self.addressEdit, 2, 2)
		mainLayout.addWidget(self.directionSelect, 2, 3)

	def setData(self, value) :
		self.variableSelect.setCurrentIndex(self.variableSelect.findText(value["varname"]))
		self.addressEdit.setText(value["address"])
		self.directionSelect.setCurrentIndex(self.directionSelect.findText(value["direction"]))

	def getData(self) :
		data = {}
		data["varname"] = self.variableSelect.currentText()
		data["address"] = self.addressEdit.text()
		data["direction"] = self.directionSelect.currentText()
		return data

	def refresh(self, dataList) :
		self.dataList = dataList
		value = self.getData()

		for count in range(self.variableSelect.count()) :
			self.variableSelect.removeItem(0)
		for data in self.dataList :
			self.variableSelect.addItem(data)
			
		self.setData(value)
		
class ConfigurationList(QMainWindow) :
	def __init__(self, ItemWidget) :
		super().__init__()
		self.ItemWidget = ItemWidget
		self.saved = True
		self.dataList = None

		# actions
		insertAction = QAction(QIcon("resources/sample.png"), "Insert", self)
		insertAction.triggered.connect(self.insertItem)
		removeAction = QAction(QIcon("resources/sample.png"), "Remove", self)
		removeAction.triggered.connect(self.removeItem)

		# layout
		self.listLayout = QListWidget()

		# toolbar
		toolbar = self.addToolBar("")
		toolbar.addAction(insertAction)
		toolbar.addAction(removeAction)

		self.setCentralWidget(self.listLayout)

	def insertItem(self) :
		if not self.dataList :
			self.errorMessage("There is no model file.")
			return None

		item = QListWidgetItem(self.listLayout)
		self.listLayout.addItem(item)
		itemWidget = self.ItemWidget(self.dataList)
		item.setSizeHint(itemWidget.sizeHint())
		itemWidget.setChangedCallback(self.changed)
		self.listLayout.setItemWidget(item, itemWidget)

		self.saved = False
		return itemWidget

	def removeItem(self) :
		for item in self.listLayout.selectedItems() :
			self.listLayout.takeItem(self.listLayout.row(item))
		self.saved = False

	def initByData(self, dataList, configList) :
		self.dataList = dataList
		for config in configList :
			itemWidget = self.insertItem()
			if itemWidget :
				itemWidget.setData(config)
		self.saved = True

	def refresh(self, dataList) :
		self.dataList = dataList
		for index in range(self.listLayout.count()) :
			item = self.listLayout.item(index)
			self.listLayout.itemWidget(item).refresh(self.dataList)

	def clear(self) :
		for count in range(self.listLayout.count()) :
			self.listLayout.takeItem(0)

	def getData(self) :
		data = []
		for index in range(self.listLayout.count()) :
			item = self.listLayout.item(index)
			data.append(self.listLayout.itemWidget(item).getData())
		self.saved = True
		return data

	def changed(self) :
		self.saved = False

	def checkSaved(self) :
		return self.saved

	def errorMessage(self, message) :
		QMessageBox.critical(self, "Error", message)

class ConfigurationEditor(QMainWindow) :
	def __init__(self, modelPath, configPath) :
		super().__init__()

		self.platformList = ResourceManager.readPlatformList()
		self.saved = True

		refreshAction = QAction(QIcon("resources/sample.png"), "Refresh", self)
		refreshAction.triggered.connect(self.refreshModel)
		toolbar = self.addToolBar("")
		toolbar.addAction(refreshAction)

		# layout
		mainwidget = QWidget()
		mainLayout = QVBoxLayout()
		platformLayout = QGridLayout()
		configurationLayout = QHBoxLayout()

		mainwidget.setLayout(mainLayout)
		mainLayout.addLayout(platformLayout)
		mainLayout.addLayout(configurationLayout)

		mainLayout.setAlignment(platformLayout, Qt.AlignTop | Qt.AlignHCenter)
		mainLayout.setAlignment(configurationLayout, Qt.AlignTop | Qt.AlignHCenter)

		# platform editor
		self.platformSelect = QComboBox()
		for platform in self.platformList.keys() :
			self.platformSelect.addItem(platform)
		self.platformSelect.setCurrentIndex(-1)
		self.platformSelect.currentIndexChanged.connect(self.platformSelected)
		self.osSelect = QComboBox()
		self.osSelect.setCurrentIndex(-1)
		self.osSelect.currentIndexChanged.connect(self.osSelected)
		self.networkSelect = QComboBox()
		self.networkSelect.setCurrentIndex(-1)
		self.networkSelect.currentIndexChanged.connect(self.networkSelected)
		self.periodEdit = QLineEdit()

		platformLayout.addWidget(QLabel("Platform"), 1, 1)
		platformLayout.addWidget(QLabel("Operating System"), 1, 2)
		platformLayout.addWidget(QLabel("Network Library"), 1, 3)
		platformLayout.addWidget(QLabel("Control Period(ns)"), 1, 4)
		platformLayout.addWidget(self.platformSelect, 2, 1)
		platformLayout.addWidget(self.osSelect, 2, 2)
		platformLayout.addWidget(self.networkSelect, 2, 3)
		platformLayout.addWidget(self.periodEdit, 2, 4)

		self.platformSelect.setMaximumWidth(150)
		self.osSelect.setMaximumWidth(150)
		self.networkSelect.setMaximumWidth(150)
		self.periodEdit.setMaximumWidth(150)

		platformLayout.setContentsMargins(10, 10, 10, 10)
		platformLayout.setHorizontalSpacing(20)
		platformLayout.setColumnMinimumWidth(1, 150)
		platformLayout.setColumnMinimumWidth(2, 150)
		platformLayout.setColumnMinimumWidth(3, 150)
		platformLayout.setColumnMinimumWidth(4, 150)
		platformLayout.setSizeConstraint(QLayout.SetFixedSize)

		# configurations
		self.taskConfiguration = ConfigurationList(TaskConfigurationItem)
		self.ioConfiguration = ConfigurationList(IOConfigurationItem)
		configurationLayout.addWidget(self.taskConfiguration)
		configurationLayout.addWidget(self.ioConfiguration)

		# initialize from data
		self.modelPath = modelPath
		self.configPath = configPath
		self.initByData()
		self.saved = True

		# initialize finished
		self.setCentralWidget(mainwidget)

	def clearSelect(self, comboBox) :
		for count in range(comboBox.count()) :
			comboBox.removeItem(0)

	def platformSelected(self, index) :
		self.clearSelect(self.osSelect)
		self.clearSelect(self.networkSelect)
		if self.platformSelect.currentText() :
			for os in self.platformList[self.platformSelect.currentText()].keys() :
				self.osSelect.addItem(os)
		self.osSelect.setCurrentIndex(-1)
		self.networkSelect.setCurrentIndex(-1)
		self.saved = False

	def osSelected(self, index) :
		self.clearSelect(self.networkSelect)
		if self.osSelect.currentText() :
			for network in self.platformList[self.platformSelect.currentText()][self.osSelect.currentText()] :
				self.networkSelect.addItem(network)
		self.networkSelect.setCurrentIndex(-1)
		self.saved = False

	def networkSelected(self, index) :
		self.saved = False

	def initByData(self) :
		try :
			file = open(self.configPath, "rb")
			self.configurationData = pickle.load(file)
			file.close()
		except :
			self.configurationData = None

		if self.configurationData :
			index = -1
			if self.configurationData.get("platform") :
				index = self.platformSelect.findText(self.configurationData["platform"])
				self.platformSelect.setCurrentIndex(index)
			if index != -1 and self.configurationData.get("os") :
				index = self.osSelect.findText(self.configurationData["os"])
				self.osSelect.setCurrentIndex(index)
			if index != -1 and self.configurationData.get("network") :
				index = self.networkSelect.findText(self.configurationData["network"])
				self.networkSelect.setCurrentIndex(index)
			if self.configurationData.get("period") :
				self.periodEdit.setText(self.configurationData["period"])

		try :
			self.model = UppaalProjectParser.parseUppaalProject(self.modelPath)
		except :
			self.model = None

		if self.model :
			templateList = [template["name"] for template in self.model["templates"]]
			variableList = [variable["name"] for variable in self.model["variables"] if variable["type"] != "clock" and variable["type"] != "chan"]
			if self.configurationData :
				self.taskConfiguration.initByData(templateList, self.configurationData["taskList"])
				self.ioConfiguration.initByData(variableList, self.configurationData["ioList"])
		else :
			self.errorMessage("There is no model file.")

	def refreshModel(self) :
		try :
			self.model = UppaalProjectParser.parseUppaalProject(self.modelPath)
		except :
			self.model = None

		if self.model :
			templateList = [template["name"] for template in self.model["templates"]]
			variableList = [variable["name"] for variable in self.model["variables"] if variable["type"] != "clock" and variable["type"] != "chan"]
			self.taskConfiguration.refresh(templateList)
			self.ioConfiguration.refresh(variableList)
		else :
			self.errorMessage("There is no model file.")

		self.saved = False

	def checkSaved(self) :
		if self.saved and self.taskConfiguration.checkSaved() and self.ioConfiguration.checkSaved() :
			return True
		else :
			return False

	def save(self, projectPath) :
		configurationData = {}
		configurationData["platform"] = self.platformSelect.currentText()
		configurationData["os"] = self.osSelect.currentText()
		configurationData["network"] = self.networkSelect.currentText()
		configurationData["period"] = self.periodEdit.text()
		configurationData["taskList"] = self.taskConfiguration.getData()
		configurationData["ioList"] = self.ioConfiguration.getData()

		file = open(os.path.join(projectPath, "sysconfig.data"), "wb")
		pickle.dump(configurationData, file)
		file.close()

		self.saved = True

	def setProjectPath(self, modelPath, configPath) :
		self.modelPath = modelPath
		self.configPath = configPath
		self.refreshModel()

	def errorMessage(self, message) :
		QMessageBox.critical(self, "Error", message)
