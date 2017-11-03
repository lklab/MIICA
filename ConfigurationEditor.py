from PyQt5.QtWidgets import QWidget, QLayout, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox, QScrollArea
from PyQt5.QtCore import Qt

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
#		mainLayout.setSizeConstraint(QLayout.SetFixedSize)

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
		self.lScroll = QScrollArea()
		self.rScroll = QScrollArea()
		configurationLayout.addWidget(self.lScroll)
		configurationLayout.addWidget(self.rScroll)
