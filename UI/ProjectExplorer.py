from PyQt5.QtWidgets import QTreeView, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from UI.Core import Icons

class ProjectExplorer(QTreeView) :
	def __init__(self) :
		super().__init__()
		self.clear()
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.setExpandsOnDoubleClick(False)
		self.doubleClicked.connect(self.doubleClickHandler)

	# private mathods
	def addItem(self, icon, name, callback) :
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

		self.rootItem = QStandardItem(Icons.Project, name)
		self.rootItem.setData(None)
		self.projectItemModel.appendRow(self.rootItem)
		index = self.projectItemModel.indexFromItem(self.rootItem)

		self.setModel(self.projectItemModel)
		self.setExpanded(index, True)

	def setModelItem(self, name, callback) :
		if self.modelItem :
			self.modelItem.setText(name)
			self.modelItem.setData(callback)
		else :
			self.modelItem = self.addItem(Icons.EditModel, name, callback)

	def setSystemConfigurationItem(self, name, callback) :
		if self.configurationItem :
			self.configurationItem.setText(name)
			self.configurationItem.setData(callback)
		else :
			self.configurationItem = self.addItem(Icons.SystemConfiguration, name, callback)

	def doubleClickHandler(self, index) :
		item = self.projectItemModel.itemFromIndex(index)
		callback = item.data()
		if callback :
			callback()
