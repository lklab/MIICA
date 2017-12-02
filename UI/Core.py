from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QIcon
import os

class Paths() :
	Resources = "Resources"
	ResourcesAbs = os.path.abspath(Resources)
	
	Icon = os.path.join(Resources, "icons")

	Project = "project.utopiia"
	Model = "Model.xml"
	SystemConfiguration = "sysconfig.data"
	ControllerData = "ctlmgr.data"

	Setting = os.path.join(Resources, "setting")
	Context = os.path.join(Setting, "context.data")
	TempProjectRoot = os.path.join(Setting, "temp_project")
	BasicModel = os.path.join(Setting, Model)

	BuildResource = os.path.join(ResourcesAbs, "build")
	PlatformList = os.path.join(BuildResource, "platform_list.xml")

	def getPlatformResourcePath(platform, targetOS) :
		return os.path.join(Paths.BuildResource, platform + "_" + targetOS)

class Icons() :
	def init() :
		Icons.Project = QIcon(os.path.join(Paths.Icon, "project.png"))

		Icons.NewProject = QIcon(os.path.join(Paths.Icon, "new_project.png"))
		Icons.OpenProject = QIcon(os.path.join(Paths.Icon, "open_project.png"))
		Icons.SaveProject = QIcon(os.path.join(Paths.Icon, "save_project.png"))
		Icons.SaveProjectAs = QIcon(os.path.join(Paths.Icon, "save_project_as.png"))

		Icons.ImportModel = QIcon(os.path.join(Paths.Icon, "import_model.png"))
		Icons.EditModel = QIcon(os.path.join(Paths.Icon, "edit_model.png"))

		Icons.SystemConfiguration = QIcon(os.path.join(Paths.Icon, "configuration.png"))
		Icons.ControllerConfiguration = QIcon(os.path.join(Paths.Icon, "controller.png"))

		Icons.Generate = QIcon(os.path.join(Paths.Icon, "generate.png"))
		Icons.Regenerate = QIcon(os.path.join(Paths.Icon, "regenerate.png"))

		Icons.Refresh = QIcon(os.path.join(Paths.Icon, "refresh.png"))
		Icons.Insert = QIcon(os.path.join(Paths.Icon, "insert.png"))
		Icons.Remove = QIcon(os.path.join(Paths.Icon, "delete.png"))

		Icons.Connect = QIcon(os.path.join(Paths.Icon, "connect.png"))
		Icons.Disconnect = QIcon(os.path.join(Paths.Icon, "disconnect.png"))
		Icons.Transmit = QIcon(os.path.join(Paths.Icon, "transmit.png"))
		Icons.Run = QIcon(os.path.join(Paths.Icon, "run.png"))
		Icons.Stop = QIcon(os.path.join(Paths.Icon, "stop.png"))

class Platform() :
	LocalPlatform = "x86_64"
	LocalOS = "Linux"

	CorrectUppaal41 = \
"""#!/usr/bin/env bash

#  
# Run this script to start UPPAAL 4.1.x.
#
"""
	CorrectUppaal40 = \
"""#!/usr/bin/env bash

#  
# Run this script to start UPPAAL 4.0.x.
#
"""
	CorrectModel41 = \
"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' \
'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
"""
	CorrectModel40 = \
"""<?xml version='1.0' encoding='utf-8'?>\
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' \
'http://www.it.uu.se/research/group/darts/uppaal/flat-1_1.dtd'>\
<nta><declaration>"""
	
	def uppaalCommand(UppaalPath, ModelPath) :
		return UppaalPath + " " + ModelPath

	def buildCommand(isLocal) :
		command = []
		if isLocal :
			command.append("cmake .")
		else :
			command.append("cmake -DCMAKE_TOOLCHAIN_FILE=./toolchain.cmake .")
		command.append("make")
		return command

class Console() :
	console = None

	def getDefaultConsole() :
		if not Console.console :
			Console.console = QTextEdit()
			Console.console.setReadOnly(True)
		return Console.console

	def print(data) :
		if Console.console :
			Console.console.setPlainText(Console.console.toPlainText() + data)
			Console.console.verticalScrollBar().setValue(Console.console.verticalScrollBar().maximum())
