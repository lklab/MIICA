from PyQt5.QtWidgets import (QWidget, QMainWindow, QLayout, QVBoxLayout,
	QHBoxLayout, QGridLayout, QListWidget, QListWidgetItem, QLabel,
	QComboBox, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class TaskConfigurationItem(QWidget) :
	def __init__(self) :
		super().__init__()

		# widget
		self.taskSelect = QComboBox()
		self.taskSelect.addItem("Task 1")
		self.taskSelect.addItem("Task 2")
		self.taskSelect.addItem("Task 3")
		self.taskSelect.currentIndexChanged.connect(self.changed)

		# layout
		mainLayout = QHBoxLayout(self)
		mainLayout.addWidget(QLabel("Task :"))
		mainLayout.addWidget(self.taskSelect)

	def getData(self) :
		return self.taskSelect.currentText()

	def changed(self, index) :
		pass
		
class ConfigurationList(QMainWindow) :
	def __init__(self, ItemWidget) :
		super().__init__()
		self.ItemWidget = ItemWidget

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
		item = QListWidgetItem(self.listLayout)
		self.listLayout.addItem(item)
		itemWidget = self.ItemWidget()
		item.setSizeHint(itemWidget.sizeHint())
		self.listLayout.setItemWidget(item, itemWidget)

	def removeItem(self) :
		for item in self.listLayout.selectedItems() :
			self.listLayout.takeItem(self.listLayout.row(item))

	def getData(self) :
		data = []
		for index in range(self.listLayout.count()) :
			item = self.listLayout.item(index)
			data.append(self.listLayout.itemWidget(item).getData())

class ConfigurationEditor(QWidget) :
	def __init__(self) :
		super().__init__()

		# layout
		mainLayout = QVBoxLayout(self)
		platformLayout = QGridLayout()
		configurationLayout = QHBoxLayout()

		mainLayout.addLayout(platformLayout)
		mainLayout.addLayout(configurationLayout)

		mainLayout.setAlignment(platformLayout, Qt.AlignTop | Qt.AlignHCenter)
		mainLayout.setAlignment(configurationLayout, Qt.AlignTop | Qt.AlignHCenter)

		# platform editor
		self.platformSelect = QComboBox()
		self.platformSelect.addItem("x86_64")
		self.platformSelect.addItem("ARM")
		self.osSelect = QComboBox()
		self.osSelect.addItem("Linux")
		self.networkSelect = QComboBox()
		self.networkSelect.addItem("Standard I/O")
		self.networkSelect.addItem("SOEM")

		platformLayout.addWidget(QLabel("Platform"), 1, 1)
		platformLayout.addWidget(QLabel("Operating System"), 1, 2)
		platformLayout.addWidget(QLabel("Network Library"), 1, 3)
		platformLayout.addWidget(self.platformSelect, 2, 1)
		platformLayout.addWidget(self.osSelect, 2, 2)
		platformLayout.addWidget(self.networkSelect, 2, 3)

		platformLayout.setContentsMargins(10, 10, 10, 10)
		platformLayout.setHorizontalSpacing(20)
		platformLayout.setColumnMinimumWidth(1, 150)
		platformLayout.setColumnMinimumWidth(2, 150)
		platformLayout.setColumnMinimumWidth(3, 150)
		platformLayout.setSizeConstraint(QLayout.SetFixedSize)

		# configurations
		self.taskConfiguration = ConfigurationList(TaskConfigurationItem)
		self.ioConfiguration = ConfigurationList(TaskConfigurationItem)
		configurationLayout.addWidget(self.taskConfiguration)
		configurationLayout.addWidget(self.ioConfiguration)

	def checkSaved(self) :
		pass
