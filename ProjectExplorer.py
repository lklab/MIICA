from PyQt5.QtWidgets import QTreeView, QAbstractItemView
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem

class ProjectExplorer(QTreeView) :
	def __init__(self) :
		QTreeView.__init__(self)
		self.clear()
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.setExpandsOnDoubleClick(False)
		self.doubleClicked.connect(self.doubleClickHandler)

	# private mathods
	def addItem(self, name, icon, callback) :
		item = QStandardItem(icon, name)
		item.setData(callback)
		self.rootItem.appendRow(item)
		return item

	# public methods
	def clear(self) :
		self.setModel(None)
		self.projectItemModel = None
		self.rootItem = None
		self.modelItem = None
		self.configurationItem = None

	def setProject(self, name) :
		self.clear()
		
		self.projectItemModel = QStandardItemModel()
		self.projectItemModel.setHorizontalHeaderLabels([name])

		self.rootItem = QStandardItem(QIcon("resources/sample.png"), name)
		self.rootItem.setData(None)
		self.projectItemModel.appendRow(self.rootItem)
		index = self.projectItemModel.indexFromItem(self.rootItem)

		self.setModel(self.projectItemModel)
		self.setExpanded(index, True)

	def setModelItem(self, callback) :
		if self.modelItem :
			self.modelItem.setData(callback)
		else :
			self.modelItem = self.addItem("Model.xml", QIcon("resources/sample.png"), callback)

	def setSystemConfigurationItem(self, callback) :
		if self.configurationItem :
			self.configurationItem.setData(callback)
		else :
			self.configurationItem = self.addItem("Configuration.xml", QIcon("resources/sample.png"), callback)

	def doubleClickHandler(self, index) :
		item = self.projectItemModel.itemFromIndex(index)
		callback = item.data()
		if callback :
			callback()
